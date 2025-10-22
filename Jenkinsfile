pipeline {
    agent any
    
    environment {
        THAITRACKING_USERNAME = credentials('thaitracking-username')
        THAITRACKING_PASSWORD = credentials('thaitracking-password')
        BACKEND_TOKEN = credentials('backend-api-token')
        BACKEND_URL = 'https://be-analytics.onrender.com/drivingdistance/bulk'
    }
    

    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Run ThaiTracking GPS Scraper') {
            steps {
                script {
                    def targetDate = params.TARGET_DATE ?: sh(script: 'date -d "yesterday" +%Y-%m-%d', returnStdout: true).trim()
                    echo "Syncing ThaiTracking GPS data for date: ${targetDate}"
                    
                    env.TARGET_DATE = targetDate
                }
                
                sh '''
                    . venv/bin/activate
                    python main.py
                '''
            }
        }
    }
}