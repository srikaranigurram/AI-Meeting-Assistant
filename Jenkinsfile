```groovy
pipeline {
    agent any

    environment {
        IMAGE_NAME = 'ai-meeting-assistant-backend'
        IMAGE_TAG = "${BUILD_NUMBER}"
        CONTAINER_NAME = 'ai_meeting_backend_ci'
        APP_PORT = '8000'

        // Configure these credentials in Jenkins:
        // JWT_SECRET_KEY and GEMINI_API_KEY
        JWT_SECRET_KEY = credentials('JWT_SECRET_KEY')
        GEMINI_API_KEY = credentials('GEMINI_API_KEY')
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code from GitHub'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv .ci_venv
                    . .ci_venv/bin/activate
                    python -m pip install --upgrade pip
                    pip install -r requirements-dev.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . .ci_venv/bin/activate

                    # Create the directory before pytest writes its report
                    mkdir -p test-reports

                    pytest -v --junitxml=test-reports/junit.xml
                '''
            }

            post {
                always {
                    junit(
                        allowEmptyResults: true,
                        testResults: 'test-reports/junit.xml'
                    )
                }
            }
        }

        stage('Build') {
            steps {
                sh '''
                    . .ci_venv/bin/activate

                    python -m py_compile main.py database.py
                    python -m py_compile models/*.py routers/*.py services/*.py

                    echo "Python syntax validation completed."
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    docker build \
                        -t ${IMAGE_NAME}:${IMAGE_TAG} \
                        -t ${IMAGE_NAME}:latest \
                        .

                    echo "Docker image build completed."
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    # Remove the previous CI container if it exists
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true

                    # Start the newly built backend container
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p ${APP_PORT}:8000 \
                        -e JWT_SECRET_KEY="${JWT_SECRET_KEY}" \
                        -e GEMINI_API_KEY="${GEMINI_API_KEY}" \
                        -e DATABASE_URL="sqlite:///./database.db" \
                        ${IMAGE_NAME}:${IMAGE_TAG}

                    # Wait for the application health endpoint
                    if ! curl \
                        --retry 10 \
                        --retry-delay 3 \
                        --retry-connrefused \
                        --fail \
                        http://localhost:${APP_PORT}/health
                    then
                        echo "Deployment health check failed."
                        docker logs ${CONTAINER_NAME} || true
                        exit 1
                    fi

                    echo "Backend health check passed."
                '''
            }
        }
    }

    post {
        always {
            echo 'Cleaning up the CI virtual environment.'
            sh 'rm -rf .ci_venv'
        }

        success {
            echo "CI/CD pipeline succeeded for build #${BUILD_NUMBER}."
        }

        failure {
            echo "CI/CD pipeline failed for build #${BUILD_NUMBER}."
        }
    }
}
