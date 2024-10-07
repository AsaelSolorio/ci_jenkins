pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                // Checkout the code from your repository
                echo 'Checking out code...'
                git branch: 'main', credentialsId: 'CREDS_jenkins', url: 'https://github.com/AsaelSolorio/ci_jenkins.git'
            }
        }

        stage('Test Docker Access') {
            steps {
                script {
                    // Check if Docker is accessible
                    echo 'Testing Docker access...'
                    sh 'docker --version'
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                // Install dependencies inside the Python Docker container
                echo 'Installing dependencies...'
                script {
                    docker.image('python:3.10.12').inside {
                        sh 'pip install -r scripts/requirements.txt'
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                // Run tests inside the Python Docker container
                echo 'Running tests...'
                script {
                    docker.image('python:3.10.12').inside {
                        sh 'pytest scripts/test_etl.py'
                    }
                }
            }
        }
    }

    post {
        always {
            // Archive CSV files generated during the tests
            echo 'Archiving CSV files...'
            archiveArtifacts artifacts: '**/*.csv', allowEmptyArchive: true
        }
    }
}
