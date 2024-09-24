pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                // Checkout the code from your repository
                git branch: 'main', credentialsId: 'github-credentials', url: 'https://github.com/AsaelSolorio/ci_jenkins.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                // Install dependencies inside the Python Docker container
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
                script {
                    docker.image('python:3.10.12').inside {
                        sh 'pytest scripts/'
                    }
                }
            }
        }
    }

    post {
        always {
            // Archive CSV files generated during the tests
            archiveArtifacts artifacts: '**/*.csv', allowEmptyArchive: true
        }
    }
}
