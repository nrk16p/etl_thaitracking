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
                    
                }
                
                sh '''
                    . venv/bin/activate
                    python main.py
                '''
            }
        }
    }
}