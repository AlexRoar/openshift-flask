
# Flask Jenkins Demo in Openshift

This demo shows how to use integrated Jenkins pipelines with Openshift. 

## Requirements: 
You need to have Openshift 3.9 or higher Up and Running.

## Scenrario 1 - Python APP - Webhooks
In this Scenario we are going to create an application in OpenShift from Git. 

### Procedure

Login via web console and create a new project named **demo-jenkins**
create a new app by browsing Languages -> python -> python
```
App name: flask1 
Repository: https://github.com/flashdumper/openshift-flask.git
```
Press create.

Navigate to Builds -> Builds -> flask1 -> Configuration.

Copy geenric Web Hook.

Now go to https://github.com/flashdumper/openshift-flask and fork it.

Once this is done to go -> settings -> hooks -> Add webhook

- Payload URL: *paste here url from Openshift Webhook*
- SSL Verification: Disabled
- Just the push events
- Active [x]
Press Add Webhook.

Now, it's time to test it out. 
Add a whitespace and push the changes to see if webhook worked properly.

## Secnario 2 - Python APP - Jenkins Pipelines

In this scenario we are going to Create Jenkins pipeline integrated with Openshift.

### Procedure
Create a new app called flask2 using the same git repo. 
Navigate to -> Add to Project -> Browse Catalog -> Languages -> python -> python
```
App name: flask2
Repository: https://github.com/flashdumper/openshift-flask.git
```
Press create.


Create a pipeline using web console -> "Add to project" -> Import YAML/JSON.

You can use either Declarative or Scripted pipeline.

**Declarative Pipeline:**
```
apiVersion: v1
kind: BuildConfig
metadata:
  name: flask-pipeline
spec:
  strategy:
    jenkinsPipelineStrategy:
      jenkinsfile: |-
        pipeline {
          agent any
          stages {
            stage('Build') {
              steps {
                script {
                  openshift.withCluster() {
                    openshift.withProject() {
                      openshift.startBuild("flask2").logs('-f')
                    }
                  }
                }
              }
            }
            stage('Test') {
              steps {
                sh "curl -s -X GET http://flask2:8080/health"
                sh "curl -s http://flask2-demo-jenkins.apps.demo.li9.com/ | grep Hello"
              }
            }
          }
        }
    type: JenkinsPipeline
```

**Scripted Pipeline:**
```
node {
    stage('Build') {
            openshift.withCluster() {
                openshift.withProject() {
                    openshift.startBuild("flask2").logs('-f')
                }       
            }
        }
    stage('Test') {
        sleep 5
        sh "curl -s http://flask2:8080/health"
        sh "curl -s http://flask2-demo-jenkins.apps.demo.li9.com/ | grep Hello"
    }
}
```

We like using Scripted pipelines because of its simplicity.

Navigate to Build -> Pipelines -> Start Pipeline

You can check logs by clicking on **View Log**. 
Use your Openshift credentials to Authenticate on the system.

## Secnario 2 - Python APP - Jenkins Promote to Prod

We are going to use our scenario from the last time and implement Blue/Green application deployment with Manual approval.

### Procedure
Create a new app called flask2 using the same git repo. 
Navigate to -> Add to Project -> Browse Catalog -> Languages -> python -> python
```
App name: flask3
Repository: https://github.com/flashdumper/openshift-flask.git
```
Press create.
 



Some Documentation:
[Openshift pipelines](https://docs.openshift.com/container-platform/3.9/dev_guide/dev_tutorials/openshift_pipeline.html)
[Openshift Jenkins Plugin](https://github.com/openshift/jenkins-client-plugin#configuring-an-openshift-cluster)

[OpenShift V3 Plugin for Jenkins](https://github.com/openshift/jenkins-plugin#common-aspects-across-the-rest-based-functions-build-steps-scm-post-build-actions)




