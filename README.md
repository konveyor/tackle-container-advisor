## Tackle Container Advisor (TCA)
### Purpose

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

For Openshift, TCA generates the following images.

	1. tomcat|https://access.redhat.com/containers/#/registry.access.redhat.com/jboss-webserver-3/webserver31-tomcat8-openshift
	2. db2|https://access.redhat.com/containers/#/cp.stg.icr.io/cp/ftm/base/ftm-db2-base

### TCA Pipeline

<img width="1000" alt="Screen Shot 2021-07-29 at 4 10 10 PM" src="https://user-images.githubusercontent.com/8302569/127559151-bc9f3176-fcc4-4032-a0b7-ba1a29212b5b.png">

The pipeline ingests raw inputs from clients data and standardizes the data to generate named entities and versions. For standardizing or normalizing raw inputs we use a tf-idf similarity based approach. To find container images we represent images in terms of named entities as well. The normalized representation helps to match legacy applications with container images to suggest the best possible recommendations.

### Running TCA's Backend API

**STEP 1 - SETUP**

In order to setup the environment and generate the resources needed by the backend API, run the bash script ``setup.sh``

```
bash setup.sh
```

**STEP 2 - CHECK SUCCESSFUL SETUP**

Do not proceed to the next step if the final output of the ``setup.sh`` bash script is not the following one:
   
```
-----------Set up for Tackle Containerzation Adviser Completed !!!---------
```

**STEP 3 - RUN THE BACKEND API**

There are two options to run the backend API. One using a bash script.

	1. bash run.sh

Two, you can directly run the docker as follows.

	1. cd aca_backend_api/
	2. docker-compose  -f 'docker-compose-api.yml' up -d --build

### Deploying TCA's Backend API on RedHat developer sandbox OpenShift cluster

	1. sh deploy.sh

### Updating TCA's Knowledge Base

If you want to make changes to TCA's Knowledge Base, please follow the instructions below.

##### Install sqlite3

	1. https://www.sqlite.org/download.html

##### Installing Anaconda3

	 1. https://docs.anaconda.com/anaconda/install/

##### Create a Conda virtual environmment with python3.8

	1. conda create --name <env-name> python=3.8
	2. conda activate <env-name>

##### Clone the TCA Repository from git as follows and enter into the parent folder

	1. git clone https://github.com/konveyor/tackle-container-advisor.git
	2. cd tackle-container-advisor

##### Setup TCA's environment by running the following

	1. sh setup.sh

##### Update TCA's Knowledge Base

For updating the TCA's Knowledge Base, enter in the *aca_db* folder. Upload the DB file in a tool such DBeaver. Once you have completed making changes, generate a new .sql file and update the existing .sql file with the new file.

##### Clean up TCA's environment by running the following and then rerun the setup.

	1. sh clean.sh
	2. sh setup.sh


### Running TCA with a new Knowledge Base

Please perform the following steps.

##### Replace the existing .sql file with the new <new_db>.sql file in the aca_db folder

##### Change the *config.ini* file in the aca_entity_standardizer folder as follows

    1. db_path = aca_db/<new_db>.db

##### Change the *config.ini*  in the aca_kg_utils folder as follows

    1. db_path = aca_db/<new_db>.db

##### Modify the *setup.sh* script to reflect the sql and db file accordingly.

	1. aca_sql_file="<new_db>.sql"
	2. aca_db_file="<new_db>.db"


##### Run the TCA's environment setup by running the following script

	1. sh setup.sh

##### Modify the *clean.sh* script to reflect the sql and db file accordingly

	1. aca_db_file="aca_kg_ce_1.0.3.db"

### Creating a New Version of the Knowledge Base

Please perform the following changes when you create a new version

##### Update all the tests and README file with the new version information in aca_backend_api

##### Change the *config.ini*  in the aca_kg_utils and aca_entity_standardizer to reflect the new version

##### Change the README file in aca_db with new version information

##### Change all the scripts (clean.sh and setup.sh) to reflect the latest version of the knowledge base



### References

* Anup K. Kalia. Tackle Containerization Advisory for Legacy Applications. (link to the video: https://www.youtube.com/watch?v=VapEooROERw, link to the slides: https://www.slideshare.net/KonveyorIO/tackle-containerization-advisor-tca-for-legacy-applications)

* Anup K. Kalia, Raghav Batta, Jin Xiao, Mihir Choudhury and Maja Vukovic. *ACA: Application Containerization Advisory Framework for Modernizing Legacy Applications*.  IEEE International Conference on Cloud Computing (Cloud) [Work-in-progress], sept, pages 1--3, 2021.
