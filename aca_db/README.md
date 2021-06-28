# Tackle containerization adviser database

##Prerequisite

sqlite3

We represent the knowledge base in terms of a database. Below we provide an entity-relationship diagram.

<img width="549" alt="Screen Shot 2021-06-08 at 1 43 29 PM" src="https://media.github.ibm.com/user/26986/files/a9bb3a00-c85f-11eb-8611-20ce3c09365e">

#generate a .db file from .sql 

``cd aca_db/``

``cat aca_kg_ce_1.0.0.sql | sqlite3 aca_kg_ce_1.0.0.db``

copy the db file to aca_entity_standardizer/aca_db and aca_kg_utils/aca_db for generating utility files and models respectively


``cp aca_kg_ce_1.0.0.db ./aca_entity_standardizer/aca_db/.``

``cp aca_kg_ce_1.0.0.db aca_kg_utils/aca_db/.``

## Tables
1. entity_types: This contains all the entity types present in our taxonomy. Under each entity type we define entities. For example, the OS entity type contains the Linux|RedHat Linux as an entity.

<img width="269" alt="Screen Shot 2021-06-08 at 1 48 30 PM" src="https://media.github.ibm.com/user/26986/files/4fbb7400-c861-11eb-837b-371341c7e0a5">

A new entry can be added as 

``INSERT INTO entity_types(entity_type_name) VALUES(?)``


2. enitities: This contains all the named entities along with their types and mappings to Wikidata or DBPedia. The scores are obtained based on an entity linking algorithm.

<img width="1091" alt="Screen Shot 2021-06-08 at 1 50 10 PM" src="https://media.github.ibm.com/user/26986/files/5cd86300-c861-11eb-8515-b39be9d5480a">

A new entry can be added as

``INSERT INTO entities(entity_name, entity_type_id, external_link) VALUES(?,?,?)``

For external link use the following format

``{'name': '', 'qid': '<QID>', 'url': 'https://www.wikidata.org/wiki/<QID>', 'score': 1}``

The QID can for a named enitity can be obtained from 

``https://www.wikidata.org/wiki/Wikidata:Main_Page``


3. entity mentions: This contains mappings of raw mentions with their entities. Each entity could have multiple mentions. For example, Apache Tomcat can be called as Tomcat or Apache Tomcat.

<img width="633" alt="Screen Shot 2021-06-08 at 1 50 25 PM" src="https://media.github.ibm.com/user/26986/files/695cbb80-c861-11eb-9a01-b380305fa501">

A new entry can be added as 

``INSERT INTO entity_mentions(entity_mention_name, entity_type_id, entity_id) VALUES(?,?,?)``
