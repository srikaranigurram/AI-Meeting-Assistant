import concurrent.futures
import json
import os
import re
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

DEFAULT_REQUEST_TIMEOUT = 10.0  # seconds per individual API attempt

PROMPT_TEMPLATE = """You are an AI meeting assistant. Analyze the provided meeting transcript and extract structured information.

Strict Instructions:
1. Analyze ONLY the provided transcript text. Do NOT invent or extrapolate facts.
2. If an assignee is not mentioned for an action item, set assigned_to to null.
3. If a deadline is not mentioned for an action item, set deadline to null.
4. If there are no decisions, return an empty list [].
5. If there are no action items, return an empty list [].
6. Output JSON ONLY. Do NOT include markdown code block formatting or extra commentary.
7. Keep the summary concise and accurate.

You must return a JSON object with the following exact key structure:
{
  "summary": "Concise summary of the meeting",
  "key_points": ["Key point 1", "Key point 2"],
  "decisions": ["Decision 1"],
  "action_items": [
    {
      "task": "Task description",
      "assigned_to": "Person Name or null",
      "deadline": "Deadline day/time or null",
      "status": "pending"
    }
  ]
}

Transcript:
"""


def _is_transient_error(e: Exception) -> bool:
    """
    Checks whether an exception represents a temporary/transient service error
    (503, 429, rate limits, timeouts, connection errors, high demand).
    """
    if isinstance(e, (TimeoutError, concurrent.futures.TimeoutError)):
        return True

    err_type = type(e).__name__.lower()
    if "timeout" in err_type or "connecterror" in err_type:
        return True

    err_str = str(e).lower()
    transient_keywords = [
        "503", "unavailable", "high demand", "spikes in demand",
        "429", "resourceexhausted", "serviceunavailable",
        "connection", "timeout", "temporarily", "try again later",
        "deadline exceeded", "gateway time-out", "504"
    ]
    return any(keyword in err_str for keyword in transient_keywords)


def _sanitize_error_message(err: Exception, api_key: str = None) -> str:
    """
    Sanitizes error messages to prevent exposing API keys or database connection secrets.
    """
    err_str = str(err)
    if api_key and api_key.strip():
        err_str = err_str.replace(api_key.strip(), "[REDACTED_API_KEY]")
    # Mask potential Google API key patterns
    err_str = re.sub(r"AIzaSy[A-Za-z0-9_\-]{33}", "[REDACTED_API_KEY]", err_str)
    # Mask potential database credentials
    err_str = re.sub(r"postgresql://[^:]+:[^@]+@", "postgresql://***:***@", err_str)
    return err_str


def _call_gemini_single_attempt(client: genai.Client, model_name: str, prompt: str, timeout_seconds: float) -> str:
    """
    Executes a single Gemini generate_content API call wrapped in a hard ThreadPoolExecutor timeout.
    """
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
    )

    def _execute():
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config,
        )
        return response.text or ""

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_execute)
        try:
            return future.result(timeout=timeout_seconds)
        except concurrent.futures.TimeoutError:
            raise TimeoutError(f"Gemini API request to model '{model_name}' timed out after {timeout_seconds} seconds.") from None


def _call_gemini_with_retries(
    client: genai.Client,
    model_name: str,
    prompt: str,
    max_retries: int = 3,
    timeout_seconds: float = DEFAULT_REQUEST_TIMEOUT
) -> str:
    """
    Calls the Gemini API with exponential backoff retries for transient errors and bounded timeouts per attempt.
    Backoff delays: 2s, 4s, 8s.
    """
    backoff_delays = [2, 4, 8]

    for attempt in range(max_retries):
        try:
            return _call_gemini_single_attempt(client, model_name, prompt, timeout_seconds=timeout_seconds)
        except Exception as e:
            if _is_transient_error(e) and attempt < max_retries - 1:
                delay = backoff_delays[attempt] if attempt < len(backoff_delays) else 8
                print(f"[RETRY] Model '{model_name}' encountered temporary error ({type(e).__name__}). Retrying ({attempt + 1}/{max_retries}) in {delay}s...")
                time.sleep(delay)
            else:
                raise e

    raise RuntimeError(f"Exhausted all {max_retries} retry attempts for model '{model_name}'.")


def process_transcript(transcript: str) -> dict:
    """
    Sends a meeting transcript to Google Gemini API with exponential backoff retries,
    bounded timeouts, and automatic fallback model support, returning structured meeting analysis.

    Args:
        transcript (str): The transcript text to process.

    Returns:
        dict: Structured analysis containing summary, key_points, decisions, action_items.

    Raises:
        ValueError: If transcript is empty or AI response is invalid JSON/schema.
        RuntimeError: If GEMINI_API_KEY is missing or API call fails after retries/fallback.
    """
    if not transcript or not str(transcript).strip():
        raise ValueError("Transcript cannot be empty.")

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not api_key.strip():
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is missing. Please set GEMINI_API_KEY in your .env file or environment."
        )

    primary_model = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
    fallback_model = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.5-flash")

    try:
        request_timeout = max(1, int(float(os.getenv("GEMINI_REQUEST_TIMEOUT", str(DEFAULT_REQUEST_TIMEOUT)))))
    except ValueError:
        request_timeout = int(DEFAULT_REQUEST_TIMEOUT)

    prompt = f"{PROMPT_TEMPLATE}\n{transcript.strip()}"

    client = genai.Client(
        api_key=api_key.strip(),
        http_options=types.HttpOptions(timeout=request_timeout)
    )
    raw_output = None

    try:
        # Attempt primary model with retries
        raw_output = _call_gemini_with_retries(client, primary_model, prompt, max_retries=3, timeout_seconds=request_timeout)
    except Exception as primary_error:
        # If primary model fails with transient error, attempt fallback model
        if _is_transient_error(primary_error) and fallback_model and fallback_model != primary_model:
            print(f"[FALLBACK] Primary model '{primary_model}' unavailable after retries. Attempting fallback model '{fallback_model}'...")
            try:
                raw_output = _call_gemini_with_retries(client, fallback_model, prompt, max_retries=1, timeout_seconds=request_timeout)
            except Exception as fallback_error:
                sanitized_error = _sanitize_error_message(fallback_error, api_key)
                raise RuntimeError(
                    f"Gemini service unavailable on primary ('{primary_model}') and fallback ('{fallback_model}') models: {sanitized_error}"
                ) from None
        else:
            sanitized_error = _sanitize_error_message(primary_error, api_key)
            raise RuntimeError(f"Gemini API request failed: {sanitized_error}") from None

    try:
        raw_output_clean = raw_output.strip()
        if raw_output_clean.startswith("```"):
            lines = raw_output_clean.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            raw_output_clean = "\n".join(lines).strip()

        start_idx = raw_output_clean.find("{")
        end_idx = raw_output_clean.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            raw_output_clean = raw_output_clean[start_idx:end_idx + 1]

        parsed_json = json.loads(raw_output_clean)
    except Exception as e:
        raise ValueError("AI model returned invalid JSON.") from e

    if not isinstance(parsed_json, dict):
        raise ValueError("AI model returned invalid JSON.")

    required_keys = {"summary", "key_points", "decisions", "action_items"}
    if not required_keys.issubset(parsed_json.keys()):
        raise ValueError("AI model returned invalid JSON.")

    if not isinstance(parsed_json["summary"], str):
        raise ValueError("AI model returned invalid JSON.")

    if not isinstance(parsed_json["key_points"], list):
        raise ValueError("AI model returned invalid JSON.")

    if not isinstance(parsed_json["decisions"], list):
        raise ValueError("AI model returned invalid JSON.")

    if not isinstance(parsed_json["action_items"], list):
        raise ValueError("AI model returned invalid JSON.")

    validated_action_items = []
    for item in parsed_json["action_items"]:
        if not isinstance(item, dict):
            raise ValueError("AI model returned invalid JSON.")

        if "task" not in item or not item["task"]:
            raise ValueError("AI model returned invalid JSON.")

        validated_item = {
            "task": str(item.get("task", "")),
            "assigned_to": item.get("assigned_to") if item.get("assigned_to") is not None else None,
            "deadline": item.get("deadline") if item.get("deadline") is not None else None,
            "status": str(item.get("status")) if item.get("status") else "pending"
        }
        validated_action_items.append(validated_item)

    parsed_json["action_items"] = validated_action_items
    return parsed_json

