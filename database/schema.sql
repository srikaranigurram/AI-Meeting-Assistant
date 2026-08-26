-- AI Meeting Assistant Database Schema
-- Compatible with PostgreSQL / Neon Cloud PostgreSQL

-- Drop tables if they exist (in reverse order of foreign key dependencies)
DROP TABLE IF EXISTS ACTION_ITEMS CASCADE;
DROP TABLE IF EXISTS DECISIONS CASCADE;
DROP TABLE IF EXISTS KEY_POINTS CASCADE;
DROP TABLE IF EXISTS MEETINGS CASCADE;

-- 1. MEETINGS Table
CREATE TABLE MEETINGS (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    meeting_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    transcript TEXT NOT NULL,
    summary TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. KEY_POINTS Table
CREATE TABLE KEY_POINTS (
    id BIGSERIAL PRIMARY KEY,
    meeting_id BIGINT NOT NULL REFERENCES MEETINGS(id) ON DELETE CASCADE,
    point TEXT NOT NULL
);

-- 3. DECISIONS Table
CREATE TABLE DECISIONS (
    id BIGSERIAL PRIMARY KEY,
    meeting_id BIGINT NOT NULL REFERENCES MEETINGS(id) ON DELETE CASCADE,
    decision TEXT NOT NULL
);

-- 4. ACTION_ITEMS Table
CREATE TABLE ACTION_ITEMS (
    id BIGSERIAL PRIMARY KEY,
    meeting_id BIGINT NOT NULL REFERENCES MEETINGS(id) ON DELETE CASCADE,
    task TEXT NOT NULL,
    assigned_to VARCHAR(255) NULL,
    deadline VARCHAR(255) NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending'
);

-- Indexes for foreign keys and queries
CREATE INDEX idx_key_points_meeting_id ON KEY_POINTS(meeting_id);
CREATE INDEX idx_decisions_meeting_id ON DECISIONS(meeting_id);
CREATE INDEX idx_action_items_meeting_id ON ACTION_ITEMS(meeting_id);
CREATE INDEX idx_meetings_created_at ON MEETINGS(created_at DESC);
