pipeline {
    agent any
    stages {
    stage('Build') {
        steps {
            script {
                openshift.withCluster() {
                    openshift.withProject() {
                        openshift.startBuild("flask-dev").logs('-f')
                    }
                }
            }
        }
    }
    stage('Test') {
        steps {
        sh "curl -s -X GET http://flask-dev:8080/health"
        sh "curl -s http://flask-dev-project3.apps.demo.li9.com/ | grep Hello"
        }
    }
    }
}
