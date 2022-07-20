## TCA's Knowledge Base Utilities

Python scripts to generate JSON from Database

### Install Anaconda3
- Follow instructions to download and install Anaconda3

### Create conda virtual environment
	# Requires python 3.8
	conda create --name <env-name> python=3.8
	conda activate <env-name>
### Clone TCA
	git clone git@github.com:konveyor/tackle-container-advisor.git

### How to use
- ``cd tackle-container-advisor``
- ``pip3 install -r requirements.txt``
- ``cd kg_utils``
- ``db`` provides the input data
- From top level folder run ``python kg_utils/kg_utils.py`` and ``python kg_utils/generator.py``
- Outputs json are saved in: ``kg/``


### Generate documentation:
- mkdir  ``docs`` && cd  ``docs``
- Run  ``sphinx-quickstart ``
- Follow  and accept default prompts. make sure you enter the project's name
- Setting up conf.py:
	* Uncomment ``import os`` and  ``import sys``
	* Uncomment and Change path: ``sys.path.insert(0, os.path.abspath('..'))``

    * In the ``# -- General configuration ---`` field, add ``extensions = ['sphinx.ext.autodoc']``

    * In the ``# -- Options for HTML output ---`` field,  add ``html_theme = 'sphinx_rtd_theme'``
 - Setting up index.rst:
 	Add ``modules``  after line 11
- Run  ``sphinx-apidoc -o . ..``
- Run  ``make html``
- Documentation is located in ``/docs/_build/html/index.html``

## TCA_image_search

Allows users to search relevant or exact container images from  DockerHub ,Quai.io , and Artifacthub.io(Community Operators OLM) registries.

## Search urls:  

  - Dockerhub
    Dockerhub repository: [Dockerhub images](https://hub.docker.com/).

   - RedHat OpenShift: [RedHat Quay](https://quay.io/search),

   - Redhat OperatorHub: [Artifact.io](https://artifacthub.io/)
  
## Getting started

#### Prerequisite
  
  - Use [TCA_KG_Aumentation](https://github.ibm.com/tca-team/TCA_KG_Augmentation) repos to augmment new entities to the database by following the instructions from the README file. You can add a single entity or a batch of entities from a csv file to the entities table.
  - Make sure you have [docker](https://docs.docker.com/engine/install/) installed locally.
 
  - The path "db\{db_version}.db", where "db_version" is the latest TCA database version and contains all entities to search(see "entity_name" table) for images.
  
  -  In VSCODE,  Open the folder in a container,  which will install all dependencies needed to run the script.

#### Input data to the search engine.
    
    Data are loaded from the entities table from the database. You may search a single entity or all entities from the database. 
 
   Sample entities table 
    
   ![This is an image](https://github.com/divsan93/tackle-container-advisor/blob/kb_expansion/images/entities.png)
    
#### Running the script
    
 ```python kg_utils/search_images.py   -e <entity_name(s)> -db db\{db_version}.db``` This loads entity(ies) from the entity_name table and searches images across all catalogues.
 
```
python kg_utils/search_images.py -h

usage: Search container images  from dockerhub , Quay.io , and Artifacthub.io

optional arguments:

  -h, --help            show this help message and exit
  
  -e ENTITY, --entity ENTITY  Enter entity name(s) from the database. i.e :-e nginx,tomcat,ubuntu or -e all ( to search all entities). Also enclose entities with                        
  
             double words in  a quote. For example: -e 'ibm i',db2,'Apache Kafka'
             
  -db DATABASE_PATH, --database_path  DATABASE_PATH    Path containing the latest tackle containerization advisor database.
  
Try $python    -e <entity_names>    -db <database_path"> or type $python  src/search_images.py --help

```

Results are saved into the following files:  ```kg_utils\image_search_kg\images.json``` , ```kg_utils\image_search_kg\operator_images.csv``` ,```kg_utils\image_search_kg\openshift_images.csv``` ,and ```kg_utils\image_search_kg\docker_images.csv``` 
 

   
### KG Augmentation

##### TCA KG Augmentation script allows a semi-automatic way of ingesting data into the TCA Knowledge Base

##### The command line script (kg_aug.py) can be executed in 2 modes:

1. Interactive - This mode can be used for processing single entry. It allows the user to choose a table by listing all the tables in the TCA database. Based on the chosen table, the user can interactively enter values for the vaious fields. All the fields are listed along with the field type (e.g.- integer, text etc.) For fields that accept only certain values, the acceptable values are also displayed along with the field name. Some automatic checks are perfomed as the user enters a value for a particular field and if the value does not match the specified type or acceptable list of values mentioned, there is a prompt to re-enter the value for that particular field.

2. Batch - Batch mode is used for processing multiple entries. The input is a csv file with multiple values that need to be entered into the database. The format to enter values in the csv is as follows: Table_name, value1, value2,..., value n

The id field for all the tables is auto generated so the user does not have to specify it. As every entry is processed there is a automatic check for dulpicate entries. If a duplicate entry is found it is skipped and not inserted into the database. For every new entity thats inserted into KG, the mentions are automatically generated from wikidata.

##### A sample csv file (input.csv) has been uploaded for reference - input.csv

### Running the script
##### To run the script you can use one of the following commands based:

1. Interactive mode: python kg_aug.py -m interactive -d 1.0.4.db
2. Batch mode: python kg_aug.py -m batch -b input.csv -d 1.0.4.db

##### The -m indicated the mode (interactive or batch), -b points to the csv file for batch processing and -d specifies the database file.

#### Usage
```
usage: kg_aug.py [-h] -m MODE -d DB_FILE [-b BATCH_FILE] [-r DEL_FILE]

modify KB by adding or deleting entities

optional arguments:
  -h, --help     show this help message and exit
  -m MODE        mode: interactive or batch
  -d DB_FILE     database file (.db) path
  -b BATCH_FILE  batch file (.txt) path
  -r DEL_FILE    entities to delete/replace list file (.csv) path
```
