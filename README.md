
# Flask Jenkins Demo in Openshift

This demo shows how to use integrated Jenkins pipelines with Openshift. 

## Requirements: 
You need to have Openshift 3.9 or higher Up and Running.

## Scenrario 1 - Python APP - Webhooks
In this Scenario we are going to create an application in OpenShift from Git. 

### Procedure

Login via web console and create a new project named **project1**
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
- 
Press Add Webhook.

Now, it's time to test it out.

Add a whitespace and push the changes to see if webhook worked properly.

```
echo " " >> README.md
git add README.md
```

## Secnario 2 - Python APP - Jenkins Pipelines

In this scenario we are going to Create Jenkins pipeline integrated with Openshift.

### Procedure
Create a new app called flask-dev using the same git repo. 
Navigate to -> Add to Project -> Browse Catalog -> Languages -> python -> python
```
App name: flask-dev
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
    type: JenkinsPipeline
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
                      openshift.startBuild("flask-dev").logs('-f')
                    }
                  }
                }
              }
            }
            stage('Test') {
              steps {
                sh "curl -s -X GET http://flask-dev:8080/health"
                sh "curl -s http://flask-dev-project1.apps.demo.li9.com/ | grep Hello"
              }
            }
          }
        }
```

**Scripted Pipeline:**
```
apiVersion: v1
kind: BuildConfig
metadata:
  name: flask-pipeline
spec:
  strategy:
    type: JenkinsPipeline
    jenkinsPipelineStrategy:
      jenkinsfile: |-
        node {
            stage('Build') {
                    openshift.withCluster() {
                        openshift.withProject() {
                            openshift.startBuild("flask-dev").logs('-f')
                        }       
                    }
                }
            stage('Test') {
                sleep 5
                sh "curl -s http://flask-dev:8080/health"
                sh "curl -s http://flask-dev-project1.apps.demo.li9.com/ | grep Hello"
            }
        }
```

We like using Scripted pipelines because of its simplicity.

Navigate to Build -> Pipelines -> Start Pipeline

You can check logs by clicking on **View Log**. 
Use your Openshift credentials to Authenticate on the system.

Now we need to integrate Jenkins with Github. You need to do the following:
- In Jenkins job, allow the job to be triggered remotely, and set token
- Go to user settings and derive user API token.
- Go back to Github and add another webhook using the following link structure https://developer-admin:{USER_TOKEN}@jenkins-project1.apps.demo.li9.com/job/project1/job/project1-flask-pipeline/build?token={JOB_TOKEN}

Once you add webhook it should trigger Jenkins job.


## Scenario 2a - Jenkinsfile from Git

In this scenario we are going to Create Jenkins pipeline downoaded from Git.

### Procedure

Create a pipeline using web console -> "Add to project" -> Import YAML/JSON.


```
apiVersion: v1
kind: BuildConfig
metadata:
  name: flask-pipeline-git
spec:
  strategy:
    type: JenkinsPipeline
    jenkinsPipelineStrategy:
      jenkinsfilePath: Jenkinsfile
  source:
    git:
      uri: "https://github.com/flashdumper/openshift-flask.git"
      ref: master
```

Navigate to Build -> Pipelines and start Pipeline called "flask-pipeline-git"
That should download Jenkinsfile instruction


## Secnario 3 - Python APP - Jenkins Promote to Prod

We are going to use our previous scenario and implement Blue/Green application deployment with Manual approval.

### Procedure
Create a new app called flask-prod using the same git repo. 
Navigate to -> Add to Project -> Browse Catalog -> Languages -> python -> python
```
App name: flask-prod
Repository: https://github.com/flashdumper/openshift-flask.git
```
Press create.

Now we need to update our job.

```
node {
    stage('Build') {
            openshift.withCluster() {
                openshift.withProject() {
                    openshift.startBuild("flask-dev").logs('-f')
                }       
            }
        }
    stage('Test') {
        sleep 5
        sh "curl -s http://flask-dev:8080/health"
        sh "curl -s http://flask-dev-project1.apps.demo.li9.com/ | grep Hello"
    }
    stage('Approve') {
        input message: "Approve Promotion to Prod?", ok: "Promote"
    }
    stage('Prod') {
        openshift.withCluster() {
            openshift.withProject() {
                openshift.startBuild("flask-prod").logs('-f')
            }       
        }
    }
}

```

Push some new changes to the Github repo and see that both Flask1 and Jenkins pipeline are triggered. If Jenkins Build and Test stages to 


## Secnario 4 - Python APP - Jenkins Promote to Prod with Environment Variables

We are going to use previous scenario and add environment variables.

### Procedure

Go to builds -> Build -> [flask1,flask-dev,flask-prod] -> Environment
- Add STAGE variables with [Demo, Development, Production] values respectively.
- Trigger webhooks by pushing the change to Github.


## Secnario 5 - Python APP - A/B deployments
We are going to use previous scenario and create a new route to show A/B type of deployments that splits traffic between **flask-dev** and **flask-prod** in 50/50 proportion.

### Procedure

Navigate to Applications -> Routes -> Create Route.
- Name: flask-ab
- Service: flask-dev
- Split across multiple services [x]
- Service: flask-prod
- Service weight: 50/50
Finally press, **Create**.


Test out that half of the requests are going to container in flask-dev and other half to flask-prod.
```
$ curl http://flask-ab-project1.apps.demo.li9.com/
... We are in <b>Production</b> ...
$ curl http://flask-ab-project1.apps.demo.li9.com/
... We are in <b>Development</b> ...
flask-dev-5-7nblp</p
$ curl http://flask-ab-project1.apps.demo.li9.com/
... We are in <b>Production</b> ...
flask-prod-3-qww6t</p
$ curl http://flask-ab-project1.apps.demo.li9.com/
... We are in <b>Development</b> ...
```


## Secnario 6 - Python APP - Running Integration tests on a separate Jenkins Slave

This scenarios show how to use node labels and custom jenkins slaves to execute code dependent commands.

We are going to build a custom Docker image to prepare for pylint and pycodestyle syntax checking.

### TODO
[Adding Slaves](http://guides-ocp-workshop.apps.vegas.openshiftworkshop.com/workshop/devops/lab/devops-custom-slave)

node (label : 'master') {
    stage('Checkout') {
        git url: 'https://github.com/flashdumper/openshift-flask.git'
    }
    stage('Syntax') {
        echo "Code Syntax Check"
       // sh pylint app.py
       // sh pycodestyle app.py
    }
    stage('Build') {
            openshift.withCluster() {
                openshift.withProject() {
                    openshift.startBuild("flask-dev").logs('-f')
                }       
            }
        }
    stage('Test') {
        sleep 5
        sh "curl -s http://flask-dev:8080/health"
        sh "curl -s http://flask-dev-project1.apps.demo.li9.com/ | grep Hello"
    }
    stage('Approve') {
        input message: "Approve Promotion to Prod?", ok: "Promote"
    }
    stage('Prod') {
        openshift.withCluster() {
            openshift.withProject() {
                openshift.startBuild("flask-prod").logs('-f')
            }       
        }
    }
}

## Secnario 8 - Python APP - HTTP vs HTTPS

In this Scenario we are going to secure the route using HTTPS and explain how 3 different types work.



Edge: - works similar to SSL offloading where Openshift router terminates HTTPS session and then creates http session with the container

```
           ---Session1---                ---Session2---
End Client ----https---- Openshift Router ----http---- Application
```

Re-encrypt: The difference between Edge and Re-encrypt that re-encrypt creates second session to the container is secured as well.
```
           ---Session1---                ---Session2---
End Client ----https---- Openshift Router ----https---- Application
```

Pass Through: End to End secure communication between end client and Application. AKA two-way authentication.  
```
          --------------Session1---------------
End Client --https-- Openshift Router --http-- Application
```

Let's check how it all works.

### Edge 
Create a new project: 
project1 -> View All projects -> Create project:
- Name: project2
- Press, **Create**.
- Click on project2

Add to Project -> Deploy image -> centos/httpd-24-centos7
Create a secure route:
Navigate to Applications -> Routes -> Create Route.
- Name: secure-edge
- Service: httpd-24-cenos7
- Port: 8080 -> 8080
- Secure route [x]
- TLS Termination: Edge
- Press, **Create**.
- Open the link that appears in the menu. In our case - https://secure-edge-project2.apps.demo.li9.com/

You should see Apache Test Page and website to be secure and verified.

### Edge 
Navigate to Applications -> Routes -> Create Route.
- Name: secure-passthrough
- Service: httpd-24-cenos7
- Port: 8443 -> 8443
- Secure route [x]
- TLS Termination: Passthrough
- Press, **Create**.
- Open the link that appears in the menu. In our case - https://secure-passthrough-project2.apps.demo.li9.com/

When you open the page it should warn you that connection is not secure. It happens because we have self-signed certificates running inside the container. 

We can definitely fix this by creating a new Container with proper certificates.

### TODO
Create a http pod with HTTPS and try out Passthrough and re-encrypt options for SSL termination.









## Documentation:
[Openshift pipelines](https://docs.openshift.com/container-platform/3.9/dev_guide/dev_tutorials/openshift_pipeline.html)
[Openshift Jenkins Plugin](https://github.com/openshift/jenkins-client-plugin#configuring-an-openshift-cluster)

[OpenShift V3 Plugin for Jenkins](https://github.com/openshift/jenkins-plugin#common-aspects-across-the-rest-based-functions-build-steps-scm-post-build-actions)




