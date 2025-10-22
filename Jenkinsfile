pipeline {
    agent any
    
    environment {
        THAITRACKING_USERNAME = credentials('thaitracking-username')
        THAITRACKING_PASSWORD = credentials('thaitracking-password')
        BACKEND_TOKEN = credentials('backend-api-token')
        BACKEND_URL = 'https://be-analytics.onrender.com/drivingdistance/bulk'
    }
    
    parameters {
        string(name: 'TARGET_DATE', defaultValue: '', description: 'Target date (YYYY-MM-DD). Leave empty for yesterday')
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
        
        stage('Install Chrome & ChromeDriver') {
            steps {
                sh '''
                    # Install Chrome if not already installed
                    if ! command -v google-chrome &> /dev/null; then
                        wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
                        sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
                        sudo apt-get update
                        sudo apt-get install -y google-chrome-stable
                    fi
                    
                    # Check Chrome version
                    google-chrome --version
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