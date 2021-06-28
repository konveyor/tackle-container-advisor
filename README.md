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


