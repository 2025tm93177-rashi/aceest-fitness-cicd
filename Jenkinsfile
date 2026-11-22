pipeline {
    agent any

    environment {
        DOCKER_REPO = "2025tm93177rashi/aceest-fitness"
        IMAGE_TAG = "v3.2.4-${BUILD_NUMBER}"
    }

    triggers {
        pollSCM('H/2 * * * *')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Unit Tests') {
            steps {
                sh 'python3 -m pytest -v'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh 'sonar-scanner'
                }
            }
        }

        stage('Build & Container Test') {
            steps {
                sh "docker build -t ${DOCKER_REPO}:${IMAGE_TAG} -t ${DOCKER_REPO}:latest ."
                sh "docker run --rm ${DOCKER_REPO}:${IMAGE_TAG} pytest -v"
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
                    sh '''
                        echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
                        docker push "${DOCKER_REPO}:${IMAGE_TAG}"
                        docker push "${DOCKER_REPO}:latest"
                    '''
                }
            }
        }
    }
}
