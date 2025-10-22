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
        
        stage('Install Chrome') {
            steps {
                sh '''
                    # Check if Chrome is already installed
                    if command -v google-chrome &> /dev/null; then
                        echo "✅ Chrome is already installed"
                        google-chrome --version
                    else
                        echo "📦 Installing Chrome..."
                        
                        # Install dependencies
                        apt-get update
                        apt-get install -y wget gnupg
                        
                        # Add Chrome repository
                        wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
                        echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
                        
                        # Install Chrome
                        apt-get update
                        apt-get install -y google-chrome-stable
                        
                        echo "✅ Chrome installed successfully"
                        google-chrome --version
                    fi
                '''
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
                sh '''
                    . venv/bin/activate
                    python main.py
                '''
            }
        }
    }
}