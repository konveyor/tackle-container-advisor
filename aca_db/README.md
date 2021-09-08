# TCA's Knowledge Base

### Prerequisites

##### Install sqlite3

	1. https://www.sqlite.org/download.html


### Entity-Relationship in TCA's Knowledge Base

We represent the knowledge base in terms of a database. Below we provide an entity-relationship diagram.

<img width="800" alt="Screen Shot 2021-07-09 at 2 06 58 PM" src="https://user-images.githubusercontent.com/8302569/125119913-bd0c3000-e0bf-11eb-9dc4-a40c5a1bf6a1.png">


### Setting up TCA's Knowledge Base

##### Generate the .db file from the .sql file.

	1. cd aca_db/
	2. cat aca_kg_ce_1.0.1.sql | sqlite3 aca_kg_ce_1.0.1.db``

##### Copy the db file to aca_entity_standardizer/aca_db and aca_kg_utils/aca_db for generating utility files and models respectively

	1. cp aca_kg_ce_1.0.1.db ./aca_entity_standardizer/aca_db/.
	2. cp aca_kg_ce_1.0.1.db aca_kg_utils/aca_db/.
	
##### Download DBeaver Community tool from the link below

	1. https://dbeaver.io/
	
##### Set the .db file path to DBeaver to view tables and data. To set right click on Database Navigator to choose *create* -> *connection* -> *SQLite*. Then set the path as follows by providing the absolute path of the .db file

	Path: /<path>/aca_kg_ce_1.0.1.db

### Table Details

**1. entity_types** 

##### This contains all the entity types present in our taxonomy. Under each entity type we define entities. For example, the OS entity type contains the Linux|RedHat Linux as an entity.

<img width="200" alt="Screen Shot 2021-06-08 at 1 48 30 PM" src="https://media.github.ibm.com/user/26986/files/4fbb7400-c861-11eb-837b-371341c7e0a5">

##### A new entry can be added as 

	INSERT INTO entity_types(entity_type_name) VALUES(?)


**2. entities** 

##### This contains all the named entities along with their types and mappings to Wikidata or DBPedia. The scores are obtained based on an entity linking algorithm.

<img width="800" alt="Screen Shot 2021-06-08 at 1 50 10 PM" src="https://media.github.ibm.com/user/26986/files/5cd86300-c861-11eb-8515-b39be9d5480a">

##### A new entry can be added as

	INSERT INTO entities(entity_name, entity_type_id, external_link) VALUES(?,?,?)

##### For external link use the following format

	{'name': '', 'qid': '<QID>', 'url': 'https://www.wikidata.org/wiki/<QID>', 'score': 1}

##### The QID can for a named enitity can be obtained from 

	https://www.wikidata.org/wiki/Wikidata:Main_Page


**3. entity mentions** 

##### This contains mappings of raw mentions with their entities. Each entity could have multiple mentions. For example, Apache Tomcat can be called as Tomcat or Apache Tomcat.

<img width="500" alt="Screen Shot 2021-06-08 at 1 50 25 PM" src="https://media.github.ibm.com/user/26986/files/695cbb80-c861-11eb-9a01-b380305fa501">

##### A new entry can be added as 

	INSERT INTO entity_mentions(entity_mention_name, entity_type_id, entity_id) VALUES(?,?,?)

**4. entity relations** 

##### This contains mappings of entities based on their compatibilities. For example, a relation might exists between Linux|* and Apache Tomcat which suggest Apache Tomcat is compatible with different variants of Linux such as RedHat Linux, Ubuntu, CentOS and so on.

<img width="800" alt="Screen Shot 2021-07-09 at 2 21 12 PM" src="https://user-images.githubusercontent.com/8302569/125120916-280a3680-e0c1-11eb-9347-8d3c62820534.png">

##### A new entry can be added as 

	INSERT INTO entity_relations(entity_parent_type_id, entity_parent_id, entity_child_type_id, entity_child_id, COTS) VALUES(?,?,?,?,?)

**5. docker base os images** 

##### This contains Docker specific base OS images. For example, RedHat Linux along with its mapping a DockerHub image.

<img width="1000" alt="Screen Shot 2021-07-09 at 2 21 35 PM" src="https://user-images.githubusercontent.com/8302569/125120953-39534300-e0c1-11eb-927b-c5527c028886.png">

##### A new entry can be added as

	INSERT INTO docker_baseos_images(container_name, OS, Docker_URL, Notes, CertOfImageAndPublisher, Certification_Status, OfficialImage, VerifiedPublisher, OpenShift_Correspondent_Image_URL, OpenShiftStatus) VALUES(?,?,?,?,?,?,?,?,?,?)


**6. openshift base os images** 

##### This contains Openshift specific base OS images. For example, RedHat Linux along with its mapping a OpenShift image.

<img width="1000" alt="Screen Shot 2021-07-09 at 2 21 52 PM" src="https://user-images.githubusercontent.com/8302569/125121014-4cfea980-e0c1-11eb-8bab-f20db5039dc6.png">

##### A new entry can be added as

	INSERT INTO openshift_baseos_images(container_name, OS, OpenShift_Correspondent_Image_URL, Notes, OpenShiftStatus, DockerImageType) VALUES(?,?,?,?,?,?)


**7. docker images** 

##### This contains Docker specific images. For example, Apache Tomcat long with its mapping a DockerHub image.

<img width="1000" alt="Screen Shot 2021-07-09 at 2 22 07 PM" src="https://user-images.githubusercontent.com/8302569/125121060-5c7df280-e0c1-11eb-9b3c-305efde20b2a.png">

##### A new entry can be added as

	INSERT INTO docker_images(container_name, OS, lang, lib, app, app_server, plugin, runlib, runtime, Docker_URL, Notes, CertOfImageAndPublisher) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)


**8. openshift images** 

##### This contains OpenShift specific images. For example, Apache Tomcat long with its mapping a OpenShift image.

<img width="1000" alt="Screen Shot 2021-07-09 at 2 22 26 PM" src="https://user-images.githubusercontent.com/8302569/125121100-6acc0e80-e0c1-11eb-9193-19297a7e1c67.png">

##### A new entry can be added as

	INSERT INTO openshift_images(container_name, OS, lang, lib, app, app_server, plugin, runlib, runtime, Docker_URL, Notes, CertOfImageAndPublisher) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
              


