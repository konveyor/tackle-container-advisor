## Purpose

Tackle Containerization Advisor takes client applications as a natural language description and recommends whether client applications can be containerized. For example, a client provides the application description as the following. 
		
		1. App1: rhel, db2, java, tomcat

The advisor takes the following steps to recommend the containerization. 

1. Assessment (supported in this release): One it does the assessment of the application where it standardizes the inputs to map them to relevant named entities present in our knowledge base. For details on knowledge base please check aca_db. For example, the inputs in App1 get mapped as the following.
		
		1. App1: rhel: Linux|RedHat Linux, db2: DB2, java: Java, tomcat: Apache Tomcat
	

2. Containerization (coming soon): It maps App1 to relevant containers in DockerHub or Openshift. For example, with DockerHub App1 has the following set of containers.
		
		1. App1: tomcat|https://hub.docker.com/_/tomcat, db2|https://hub.docker.com/r/ibmcom/db2


### Install Anaconda3 
	-Follow instructions to download and install Anaconda3 [doc](https://docs.anaconda.com/anaconda/install/)

### Create a Conda virtual environmment with python3.8

	conda create --name <env-name> python=3.8
	conda activate <env-name>

### Instructions to setup the Tackle Containerization Adviser

Below we mention the process to generate prequisite for tackle containerization adviser. Note the current release only support assessment.


<img width="707" alt="Screen Shot 2021-06-09 at 11 43 33 AM" src="https://media.github.ibm.com/user/26986/files/27428100-c918-11eb-9f5e-60ed9d42216e">

1. For setting up the tackle containerization advisor please run

	``sh setup.sh``

This step generate several files such as DB, utilities, and models.

2. For running the backend service, please run

	``sh run.sh``

3. For cleaning all the generated files

	``sh clean.sh``


### Running Tackle Containerization Adviser with a new DB

Please perform the following steps.

1. In the aca_db folder add a new new_db.sql file

2. In the aca_entity_standardizer folder, change the config.ini file as follows

    db_path = aca_db/new_db.db

3. In the aca_kg_utils folder, change the config.ini as follows

    db_path = aca_db/new_db.db

4. Then before runing the following, please modify the script to reflect the sql and db file accordingly.

    ``sh setup.sh``
    
5. In case of clean, please modify the script to reflect the sql and db file accordingly.


