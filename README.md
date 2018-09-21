
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
App name: flask-demo 
Repository: https://github.com/flashdumper/openshift-flask.git
```
Press create.

Navigate to Builds -> Builds -> flask-demo -> Configuration.

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



Push some new changes to the Github repo and see that both flask-demo and Jenkins pipeline are triggered. If Jenkins Build and Test stages to 


## Secnario 4 - Python APP - Jenkins Promote to Prod with Environment Variables

We use previous scenario and add environment variables.

### Procedure

Go to builds -> Build -> [flask-demo,flask-dev,flask-prod] -> Environment
- Add STAGE variables with [Demo, Development, Production] values respectively.
- Trigger webhooks by pushing the change to Github.


## Secnario 4a - Python APP - Using Secrets for Environment variables

We use previous scenario and move the values of STAGE environment to Secrets.

### Procedure

### TODO
<!-- -->

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
$ curl http://flask-ab-project1.apps.demo.li9.com/
... We are in <b>Production</b> ...
$ curl http://flask-ab-project1.apps.demo.li9.com/
... We are in <b>Development</b> ...
```


## Secnario 6 - Python APP - Running Integration tests on Dynamic Jenkins Slaves

This scenarios show how to use node labels and custom jenkins slaves to execute code dependent commands.

We are going to build a custom Docker image to prepare for pylint and pycodestyle syntax checking.

### High level overview

- Create a docker image with required packagers including pylint and pycodestyle
- Save it to registry
- Configure Jenkins for dynamic slaves

### Procedure


Search and pull httpd docker image
```
docker search jenkins
docker pull openshift/jenkins-slave-base-centos7
```

Create a Dockerfile to modify httpd image 
$ cat Dockerfile
```
FROM openshift/jenkins-slave-base-centos7

RUN yum install -y epel-release &&\
    yum install -y python2-pip &&\
    pip install --upgrade pip && \
    pip install pylint pycodestyle Flask
```

Build a new image
```
docker build -t jslave-python .
```

Push docker image to registry:
```
docker tag jslave-python flashdumper/jslave-python
docker push flashdumper/jslave-python
```

Go to Jenkins -> Manage Jenkins -> Configure System
Add new Pod Template: 
- Name: python
- Label: python

Then Add container -> Container Template:
- Name: jnlp
- Docker image: docker.io/flashdumper/jslave-python
- Always pull image: Unchecked []
- Working Directory: /tmp
- Command to run: 
- Arguments to pass to the command: ${computer.jnlpmac} ${computer.name}
- Allocate pseudo-TTY: Checked [x]
- Timeout in seconds for Jenkins connection: 100

Click Save or Apply.


Add to Project -> Import from JSON/YAML
```
apiVersion: v1
kind: BuildConfig
metadata:
  name: pipeline-unit
spec:
  strategy:
    type: JenkinsPipeline
    jenkinsPipelineStrategy:
      jenkinsfile: |-
        node (label : 'python') {
            stage('Checkout') {
                git url: 'https://github.com/flashdumper/openshift-flask.git'
            }
            stage('Syntax') {
                echo "Code Syntax Check"
                sh "pylint app.py"
                sh "pycodestyle app.py"
            }
        }
        node (label : 'master') {
            stage('Build') {
                    openshift.withCluster() {
                        openshift.withProject() {
                            openshift.startBuild("flask-dev").logs('-f')
                        }       
                    }
                }
            stage('End-to-End') {
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
Start new pipeline by navigating to -> Build -> Pipeline -> pipeline-unit -> Start pipeline 
You can log into Jenkins and Check that jenkins slave nodes are being dynamically created.
Also note that different stages are executed on differnent jenkins nodes.


## Scenario 6a - Pipeline with Parallel tasks 

This scenario extends the old 

### Procedure

Add to Project -> Import from JSON/YAML
```
apiVersion: v1
kind: BuildConfig
metadata:
  name: pipeline-unit
spec:
  strategy:
    type: JenkinsPipeline
    jenkinsPipelineStrategy:
      jenkinsfile: |-
        node (label : 'python') {
            stage('Checkout') {
                git url: 'https://github.com/flashdumper/openshift-flask.git'
            }
            stage("Parallel Tasks") {
                parallel(
                    "Test1": {
                        echo "Code Syntax Check"
                    },
                    "Test2": {
                        sh "pylint app.py"
                    },
                    "Test3": {
                        sh "pycodestyle app.py"
                    }
                )
            }
        }
        node (label : 'master') {
            stage('Build') {
                    openshift.withCluster() {
                        openshift.withProject() {
                            openshift.startBuild("flask-dev").logs('-f')
                        }       
                    }
                }
            stage('End-to-End') {
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
                        openshift.tag("project1/flask-dev:latest", "project1/flask-prod:prod")
                    }       
                }
            }
        }
```



## Secnario 7 - Python APP - HTTP vs HTTPS

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

### Paththrough 
Navigate to Applications -> Routes -> Create Route.
- Name: secure-passthrough
- Service: httpd-24-cenos7
- Port: 8443 -> 8443
- Secure route [x]
- TLS Termination: Passthrough
- Press, **Create**.
- Open the link that appears in the menu. In our case - https://secure-passthrough-project2.apps.demo.li9.com/

When you open the page it should warn you that connection is not secure. It happens because we have self-signed certificates running inside the container. 


## Secnario 7a - Python APP - HTTPS passthrough with right certs


We can definitely fix this by creating a new Container with proper certificates.

Search and pull httpd docker image
```
docker search centos/httpd
docker pull centos/httpd-24-centos7
```

Create a Dockerfile to modify httpd image 
```
$ cat Dockerfile
FROM centos/httpd-24-centos7

RUN sed -ie 's/^#SSLCertificate/SSLCertificate/g' /etc/httpd/conf.d/ssl.conf

COPY certs/localhost.crt /etc/pki/tls/certs/localhost.crt
COPY certs/localhost.key /etc/pki/tls/private/localhost.key
COPY certs/server-chain.crt /etc/pki/tls/certs/server-chain.crt
```

Create certs directory and copy there your valid certificates.
```
$ mkdir certs
$ cp <certs_dir> .
$ ls -la 
-rwxr-xr-x@ 1 dzuev  staff  2244 Aug 24 22:39 localhost.crt
-rwxr-xr-x@ 1 dzuev  staff  1679 Aug 24 22:39 localhost.key
-rwxr-xr-x@ 1 dzuev  staff  3892 Aug 24 22:39 server-chain.crt
```

Build a new image
```
docker build -t httpd-certs .
```

Verify that it works 
```
docker run -d -p 8080:8080 -p 8443:8443 --name httpd-certs httpd-certs
```

Login to your openshift registry
```
sudo docker login -u user -p password registry.apps.demo.li9.com
```

Push **httpd_certs** image to the registry
```
docker tag httpd_certs registry.apps.demo.li9.com/project2/httpd-certs
docker push registry.apps.demo.li9.com/project2/httpd-certs
```

Create an app from the image we just pushed. 
Login to Openshift web-console -> Add to project -> Deploy Iamge:
- Image Stream Tag [x]
- Project: Project2 
- Image Stream: httpd-certs
- Tag: latest
- Press enter
- Deploy

When the application is deployed. Create a route navigating to Applications -> Route -> Create Route:
- Name: httpd-certs-passthrough
- Service: httpd-certs
- Target Port: 8443 -> 8443 
- Secure route [x]
- TLS Termination: passthrough
- Create 
- Open the URL: https://httpd-certs-passthrough-project2.apps.demo.li9.com


### TODO
<!-- Re-encrypt. -->

Internal OpenShift registry route uses re-encrypt.


## Secnario 8 - Python APP - Autoscaling

In this Scenario we are going to secure the route using Autoscaling and explain how 3 different types work.

### Procedure

TODO:

Enable autoscaler: 
- Min pods: 2 
- Max pods: 5
- Cupu req: 15%

Reqourse limits: 
- Limits: 200mcore, 100mib

Healthchecks:
- Path: /health
- Delay: 10s
- Timeout: 1s

Once Auto-scaling works, You can generate some traffic your favourite benchmarking tool like ab or wrk:
- wrk -c 2000 -d 100s -t 500 https://flask-demo-project1.apps.demo.li9.com/
- ab -n 100000 -c 1000 https://flask-demo-project1.apps.demo.li9.com/
- wait for a few minutes to see that amount of pods are increasing


## Secnario 9 - Python APP - App from Dockerfile

In this scenarios we are going to build OpenShift flask application from Dockerfile.

### High Level Overview:

- Create a Dockerfile with all the required packages and instrcutions 
- Run app with **oc new-app** command to create application 
- expose application externally with **oc expose** command  


### Procedure

In order to create an application from Dockerfile and run it in OpenShift, first thing we need to do is write a new Dockerfile. You can either create Dockerfile using instructions below, or download from [here](https://github.com/flashdumper/openshift-dockerfile.git). All the other files are also located in that Git repository.

```
$ cat Dockerfile
FROM centos

COPY requirements.txt /tmp/
COPY app.py /opt/

RUN yum install -y epel-release &&\
    yum install -y python2-pip python34-pip python34 &&\
    pip install --upgrade pip &&\
    pip3 install -r /tmp/requirements.txt &&\
    chown -R 1001:0 /opt/ &&\
    chmod -R g=u /opt/

USER 1001

WORKDIR /opt/
CMD ["python3","app.py"]
```

Finally, use Openshift oc CLI and run the following command:
```
oc new-app https://github.com/flashdumper/openshift-dockerfile.git --name dockerfile
```
Once application is up and running we need to expose it expternally using **oc expose** commands:
```
oc expose dc/dockerfile --port 8080
oc expose svc --hostname dockerfile.apps.lab.atap.xyz dockerfile
```

Open your browser and navigate to http://dockerfile.apps.lab.atap.xyz/ or run **curl http://dockerfile.apps.lab.atap.xyz/** command

## Secnario 10 - Python APP - Create S2I image

In this scenario we are going to show you how to create and use S2I image to run get flask application up and running.

### High level overview of this secnario:
1. Find, pull and scan initial Docker image. 
2. Create .s2i folder with proper structure settings
    - s2i create backbone dirs (s2i create)
    - provide assemble and run scripts
3. Build a new s2i images based of the initial one
    - Create Dockerfile
    - COPY ./.s2i/bin /usr/libexec/s2i
    - CMD ["usage"]
4. Test and verify s2i image  (s2i build)
5. Push s2i image to registry (docker tag, docker push)
6. Push s2i image to imagestream (oc import-image)
7. Run code app with s2i image (oc new-app imagesteam~URL)

When **oc new-app** is executed, imagestream is run and code pulled inside the working directory. 

### Modifying s2i builds
Create .s2i/bin dir in git repo
use assemble/run files 

### Requirements 

You might need to install s2i tool to work build s2i images.
Source code with installation instructions located on [Github](https://github.com/openshift/source-to-image/releases/download/v1.1.10/source-to-image-v1.1.10-27f0729d-linux-amd64.tar.gz)

### Procedure 

Create S2I template using **s2i create** command

```
s2i create centos centos
cd centos
docker build -t centos-s2i .
# s2i build src centos-s2i centos-s2i
s2i build test/test-app centos-s2i centos-test
docker run -d centos-test

docker tag centos-s2i registry.demo.li9.com:5000/centos-s2i
docker push registry.demo.li9.com:5000/centos-s2i
oc import-image centos-s2i --from registry.demo.li9.com:5000/centos-s2i --confirm --insecure=true
oc new-app --name centos-s2i centos-s2i~git_repository

```


On master1 find a proper image in the redhat registry and scan for vulnerabilities.
```
docker search registry.access.redhat.com:443/s2i-core-rhel7
atomic scan registry.access.redhat.com:443/s2i-core-rhel7
```

Image is fine, we can proceed with creating our own image 
Pull and run this 
```
docker run registry.access.redhat.com:443/s2i-core-rhel7
```

<!-- 
## Documentation:
[Openshift pipelines](https://docs.openshift.com/container-platform/3.9/dev_guide/dev_tutorials/openshift_pipeline.html)
[Openshift Jenkins Plugin](https://github.com/openshift/jenkins-client-plugin#configuring-an-openshift-cluster)

[OpenShift V3 Plugin for Jenkins](https://github.com/openshift/jenkins-plugin#common-aspects-across-the-rest-based-functions-build-steps-scm-post-build-actions)
 -->



