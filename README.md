# Tackle Container Advisor (TCA)

## Purpose

TCA takes client applications as a natural language description and recommends whether client applications can be containerized. For example, a client can provide the application description as the following.

```
1. App1: rhel, db2, java, tomcat
```


TCA takes the following steps to recommend the containerization.

1. **Assessment**: It assesses the application to standardize the inputs to relevant named entities present in our knowledge base. For details on the knowledge base please check the *aca_db* folder. For example, the inputs in *App1* get mapped as the following named entities.

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

<img width="1000" alt="Screen Shot 2021-07-29 at 4 10 10 PM" src="https://user-images.githubusercontent.com/8302569/127559151-bc9f3176-fcc4-4032-a0b7-ba1a29212b5b.png">

The pipeline ingests raw inputs from clients data and standardizes the data to generate named entities and versions. For standardizing or normalizing raw inputs we use a tf-idf similarity based approach. To find container images we represent images in terms of named entities as well. The normalized representation helps to match legacy applications with container images to suggest the best possible recommendations.

## Setting up your environment

You cannot run this code without having a proper Python 3.8 environment first. Even the setup requires Python 3. We recommend that you follow the instructions in the [Developer's Guide](docs/development.md) before proceeding further.

## Running the TCA Backend API

**STEP 1 - SETUP**

In order to setup the environment and generate the resources needed by the backend API, run the bash script ``setup.sh``

```bash
bash setup.sh
```

**STEP 2 - CHECK SUCCESSFUL SETUP**

Do not proceed to the next step if the final output of the ``setup.sh`` bash script is not the following one:
   
```bash
-----------Set up for Tackle Containerzation Adviser Completed !!!---------
```

**STEP 3 - RUN THE BACKEND API**

There are two options to run the backend API. One using a bash script.

```bash
bash run.sh
```

Two, you can directly run the docker as follows.

```bash
cd aca_backend_api/
docker-compose  -f 'docker-compose-api.yml' up -d --build
```

### Deploying TCA's Backend API on RedHat developer sandbox OpenShift cluster

```bash
bash deploy.sh
```

## Updating TCA's Knowledge Base

If you want to make changes to TCA's Knowledge Base, make sure that you have created a proper development environment by following the setup procedure in the [Developer's Guide](docs/development.md) and then  please follow the instructions below.

### Setup TCA's environment by running the following

```bash
bash setup.sh
```

### Update TCA's Knowledge Base

For updating the TCA's Knowledge Base, enter in the *aca_db* folder. Upload the DB file in a tool such DBeaver. Once you have completed making changes, generate a new .sql file and update the existing .sql file with the new file.

### Clean up TCA's environment by running the following and then rerun the setup.

```bash
bash clean.sh
bash setup.sh
```

### Running TCA with a new Knowledge Base

Please perform the following steps.

1. Replace the existing .sql file with the new <new_db>.sql file in the aca_db folder

1. Change the *config.ini* file in the aca_entity_standardizer folder as follows

    db_path = aca_db/<new_db>.db

1. Change the *config.ini*  in the aca_kg_utils folder as follows

    db_path = aca_db/<new_db>.db

1. Modify the *setup.sh* script to reflect the sql and db file accordingly.

	aca_sql_file="<new_db>.sql"
	aca_db_file="<new_db>.db"


#### Run the TCA's environment setup by running the following script

```bash
bash setup.sh
```

#### Modify the *clean.sh* script to reflect the sql and db file accordingly

	aca_db_file="aca_kg_ce_1.0.3.db"

### Creating a New Version of the Knowledge Base

Please perform the following changes when you create a new version

1. Update all the tests and README file with the new version information in aca_backend_api

1. Change the *config.ini*  in the `aca_kg_utils` and `aca_entity_standardizer to reflect the new version

1. Change the README file in aca_db with new version information

1. Change all the scripts (clean.sh and setup.sh) to reflect the latest version of the knowledge base

## References

* Anup K. Kalia. Tackle Containerization Advisory for Legacy Applications. (link to the video: https://www.youtube.com/watch?v=VapEooROERw, link to the slides: https://www.slideshare.net/KonveyorIO/tackle-containerization-advisor-tca-for-legacy-applications)

* Anup K. Kalia, Raghav Batta, Jin Xiao, Mihir Choudhury and Maja Vukovic. *ACA: Application Containerization Advisory Framework for Modernizing Legacy Applications*.  IEEE International Conference on Cloud Computing (Cloud) [Work-in-progress], sept, pages 1--3, 2021.
