# TCA's Knowledge Base

#####[Back to main page] (#https://github.com/divsan93/tackle-container-advisor/tree/update_docs#TCA-Pipeline)

## Table of Contents
1. [Prerequisite](#Prerequisites)
2. [ER DIAGRAM](#Entity-Relationship-in-Knowledge-Base)
3. [Knowledge Base Setup](#Setting-up-the-Knowledge-Base)
4. [Table Details](#Table-Details)

### Prerequisites

##### Install sqlite3

	1. https://www.sqlite.org/download.html


### Entity Relationship in Knowledge Base

We represent the knowledge base in terms of a database. Below we provide an entity-relationship diagram.

<img width="800" alt="ER_DIAGRAM" src="https://github.com/konveyor/tackle-container-advisor/blob/main/images/ER_diagram.png">


### Setting up the Knowledge Base

##### Generate the .db file from the .sql file.

	1. cd db/
	2. cat 1.0.4.sql | sqlite3 1.0.4.db``

##### Download DBeaver Community tool from the link below

	1. https://dbeaver.io/

##### Set the .db file path to DBeaver to view tables and data. To set right click on Database Navigator to choose *create* -> *connection* -> *SQLite*. Then set the path as follows by providing the absolute path of the .db file

	Path: /<path>/1.0.4.db

### Table Details

**1. entity_types**

##### This contains all the entity types present in our taxonomy. Under each entity type we define entities. For example, the OS entity type contains the Linux|RedHat Linux as an entity.

<img width="200" alt="Entity Types" src="https://github.com/konveyor/tackle-container-advisor/blob/main/images/entity_types.png">

##### A new entry can be added as

	INSERT INTO entity_types(entity_type_name) VALUES(?)


**2. entities**

##### This contains all the named entities along with their types and mappings to Wikidata or DBPedia. The scores are obtained based on an entity linking algorithm.

<img width="800" alt="Entities" src="https://github.com/konveyor/tackle-container-advisor/blob/main/images/entities.png">

##### A new entry can be added as

	INSERT INTO entities(entity_name, entity_type_id, external_link) VALUES(?,?,?)

##### For external link use the following format

	{'name': '', 'qid': '<QID>', 'url': 'https://www.wikidata.org/wiki/<QID>', 'score': 1}

##### The QID can for a named enitity can be obtained from

	https://www.wikidata.org/wiki/Wikidata:Main_Page


**3. entity mentions**

##### This contains mappings of raw mentions with their entities. Each entity could have multiple mentions. For example, Apache Tomcat can be called as Tomcat or Apache Tomcat.

<img width="500" alt="Entity Mentions" src="https://github.com/konveyor/tackle-container-advisor/blob/main/images/entity_mentions.png">

##### A new entry can be added as

	INSERT INTO entity_mentions(entity_mention_name, entity_type_id, entity_id) VALUES(?,?,?)

**4. entity relations**

##### This contains mappings of entities based on their compatibilities. For example, a relation might exists between Linux|* and Apache Tomcat which suggest Apache Tomcat is compatible with different variants of Linux such as RedHat Linux, Ubuntu, CentOS and so on.

<img width="800" alt="Entity Relations" src="https://github.com/konveyor/tackle-container-advisor/blob/main/images/operator_images.png">

##### A new entry can be added as

	INSERT INTO entity_relations(entity_parent_type_id, entity_parent_id, entity_child_type_id, entity_child_id, COTS) VALUES(?,?,?,?,?)

**5. docker base os images**

##### This contains Docker specific base OS images. For example, RedHat Linux along with its mapping a DockerHub image.

<img width="1000" alt="Docker Base OS Images" src="https://github.com/konveyor/tackle-container-advisor/blob/main/images/docker_baseos.png">

##### A new entry can be added as

	INSERT INTO docker_baseos_images(container_name, OS, Docker_URL, Notes, CertOfImageAndPublisher, Certification_Status, OfficialImage, VerifiedPublisher, OpenShift_Correspondent_Image_URL, OpenShiftStatus) VALUES(?,?,?,?,?,?,?,?,?,?)


**6. openshift base os images**

##### This contains Openshift specific base OS images. For example, RedHat Linux along with its mapping a OpenShift image.

<img width="1000" alt="Openshift Base OS Images" src="https://github.com/konveyor/tackle-container-advisor/blob/main/images/OS_baseos.png">

##### A new entry can be added as

	INSERT INTO openshift_baseos_images(container_name, OS, OpenShift_Correspondent_Image_URL, Notes, OpenShiftStatus, DockerImageType) VALUES(?,?,?,?,?,?)


**7. docker images**

##### This contains Docker specific images. For example, Apache Tomcat long with its mapping a DockerHub image.

<img width="1000" alt="Docker Images" src="https://github.com/konveyor/tackle-container-advisor/blob/main/images/docker_images.png">

##### A new entry can be added as

	INSERT INTO docker_images(container_name, OS, lang, lib, app, app_server, plugin, runlib, runtime, Docker_URL, Notes, CertOfImageAndPublisher) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)


**8. openshift images**

##### This contains OpenShift specific images. For example, Apache Tomcat long with its mapping a OpenShift image.

<img width="1000" alt="Openshift Images" src="https://github.com/konveyor/tackle-container-advisor/blob/main/images/OS_images.png">

##### A new entry can be added as

	INSERT INTO openshift_images(container_name, OS, lang, lib, app, app_server, plugin, runlib, runtime, Docker_URL, Notes, CertOfImageAndPublisher) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)

**9. entity versions**
##### This contains versions and licensing costs for all entities.

<img width="1000" alt="entity_versions" src="https://github.com/konveyor/tackle-container-advisor/blob/main/images/entity_versions.png">

##### A new entry can be added as
        INSERT INTO entity_versions (id, entity_id, version, release_date, end_date, cost)  VALUES (?,?,?,?,?,?)

**10. docker environment variable**
##### This contains environment variables for all docker images.

<img width="1000" alt="Docker_env_var" src="https://github.com/konveyor/tackle-container-advisor/blob/main/images/docker_env.png">


##### A new entry can be added as
	INSERT  INTO docker_environment_variables(Environment_Variables, Container_Name, Required, Default_Values) VALUES(?,?,?,?)


**11. operator images**
##### This contains operator specific images. For example, Postgresql along with its mapping a operator image

<img width="1000" alt="operators" src="https://github.com/konveyor/tackle-container-advisor/blob/main/images/operator_images.png">

##### A new entry can be added as
	INSERT INTO operator_images(container_name, OS, lang, lib, app, app_server, plugin, runlib, runtime, Operator_Correspondent_Image_URL, Operator_Repository) VALUES(?,?,?,?,?,?,?,?,?,?,?)
