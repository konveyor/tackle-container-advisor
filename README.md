# Tackle Container Advisor (TCA)

## Purpose

TCA takes client applications as a natural language description and recommends whether client applications can be containerized. For example, a client can provide the application description as the following.

```
1. App1: rhel, db2, java, tomcat
```


TCA takes the following steps to recommend the containerization.

1. **Assessment**: It assesses the application to standardize the inputs to relevant named entities present in our knowledge base. For details on the knowledge base please check the *db* folder. For example, the inputs in *App1* get mapped as the following named entities.

```
1. App1: rhel: Linux|RedHat Linux, db2: DB2, java: Java, tomcat: Apache Tomcat
```

2. **Containerization**: First, it recommends whether *App1* can be containerized, partially containerized, or kept as it is. Then if App1 is recommended as containerized or partially containerized, TCA generates container images based on DockerHub or Openshift. For example, if a user decides to generate DockerHub related images, then TCA generates the following images.

```
1. tomcat|https://hub.docker.com/_/tomcat
2. db2|https://hub.docker.com/r/ibmcom/db2
```

For OpenShift, TCA generates the following images.

	1. tomcat|https://access.redhat.com/containers/#/registry.access.redhat.com/jboss-webserver-3/webserver31-tomcat8-openshift
	2. db2|https://access.redhat.com/containers/#/cp.stg.icr.io/cp/ftm/base/ftm-db2-base

## TCA Pipeline

<img width="1000" alt="TCA Pipeline" src=https://github.com/konveyor/tackle-container-advisor/blob/main/images/tca_pipeline.png>

The pipeline ingests raw inputs from clients data and standardizes the data to generate named entities and versions. For standardizing or normalizing raw inputs we use a tf-idf similarity based approach. To find container images we represent images in terms of named entities as well. The normalized representation helps to match legacy applications with container images to suggest the best possible recommendations.

## Setting up your environment

Requires Python >= 3.6 environment. You cannot run this code without having a proper
Python environment first. We recommend that you follow the instructions
in the [Developer's Guide](docs/development.md) before proceeding further.

## Running TCA as a service

There are 4 options for deploying TCA as a service.

1. Install the service requirements and start the service from command line.

Requires *gunicorn* standalone installation on your system.
```
bash setup.sh
gunicorn --workers=2 --threads=500 --timeout 300 service:app
OR
waitress-serve --listen=*:8000 service:app
```

2. Running the service as a container.

Using a bash script.
```
bash run.sh
```
Using command line.
```
docker-compose  -f 'docker-compose-api.yml' up -d --build
```

3. Running the service in a virtual machine using vagrant.
```
vagrant up
vagrant ssh
cd /vagrant
bash run.sh
```

4. Deploy the container on Redhat Openshift Container Platform.

```
bash deploy.sh
```

## Run a performance test for TCA service
A performance test measures the response time of TCA service under
various load conditions. Before running
performance test, update *config/test.ini* with the hostname
and port where TCA service has been deployed

```
python test/performance/run_payload.py <#users> <#applications/user>
```

## Running TCA with a new version of Knowledge Base

Please perform the following steps.

1. Replace the existing .sql file with the new <new_db>.sql file in the db folder

2. Change the *common.ini* file in the config folder as follows

    version = <new_db>

3. Modify the *setup.sh* and *clean.sh* scripts to reflect the version accordingly.

    version=<new_db>

4. Re-run *setup.sh* and then deploy the service.


## References

* Anup K. Kalia. Tackle Containerization Advisory for Legacy Applications. (link to the video: https://www.youtube.com/watch?v=VapEooROERw, link to the slides: https://www.slideshare.net/KonveyorIO/tackle-containerization-advisor-tca-for-legacy-applications)

* Anup K. Kalia, Raghav Batta, Jin Xiao, Mihir Choudhury and Maja Vukovic. *ACA: Application Containerization Advisory Framework for Modernizing Legacy Applications*.  IEEE International Conference on Cloud Computing (Cloud) [Work-in-progress], sept, pages 1--3, 2021.
