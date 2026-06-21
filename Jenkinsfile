// ═══════════════════════════════════════════════════════════════
// SentinelX — Jenkins CI/CD Pipeline
// ═══════════════════════════════════════════════════════════════
// Triggers on GitHub push: checks out code, builds Docker
// containers, starts the application, and verifies deployment.
// ═══════════════════════════════════════════════════════════════

pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo '📥 Checking out source code from GitHub...'
                git 'https://github.com/siddhant-jadhav/SentinelX.git'
            }
        }

        stage('Verify Repository') {
            steps {
                echo '📂 Verifying repository contents...'
                sh 'pwd'
                sh 'ls -la'
            }
        }

        // stage('Build Docker Images') {
        //     steps {
        //         echo '🐳 Building Docker containers...'
        //         sh 'docker compose build'
        //     }
        // }

        // stage('Start Application') {
        //     steps {
        //         echo '🚀 Starting SentinelX application...'
        //         sh 'docker compose up -d'
        //         sh 'sleep 10'
        //     }
        // }

        // stage('Verify Deployment') {
        //     steps {
        //         echo '✅ Verifying running containers...'
        //         sh 'docker compose ps'
        //     }
        // }
    }

    post {
        success {
            echo '✅ SentinelX pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed — check logs for details.'
        }
    }
}