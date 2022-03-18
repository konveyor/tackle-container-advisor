#!/bin/bash

######################################################################
######################################################################
##     SETUP SCRIPT FOR TACKLE CONTAINER ADVISOR ENVIRONMENT
######################################################################
######################################################################

echo "+---------------------------------------------------------+"
echo "|---------Setting up Tackle Containerzation Adviser-------|"
echo "+---------------------------------------------------------+"
aca_sql_file="aca_kg_ce_1.0.3.sql"
aca_db_file="aca_kg_ce_1.0.3.db"

echo "------------------Checking Dependencies--------------------"
# Check to make sure sqlite3 is installed
if ! command -v sqlite3 &> /dev/null
then
    echo "**** ERROR: sqlite3 command could not be found. Cannot continue."
    exit 1
fi

# Check to make sure python is installed
if ! command -v python &> /dev/null
then
    echo "**** ERROR: python command could not be found. Cannot continue."
    exit 1
else
    python -m pip install --upgrade pip wheel
fi

# Check to make sure pip3 is installed
if ! command -v pip3 &> /dev/null
then
    echo "**** ERROR: pip3 command could not be found. Cannot continue."
    exit 1
fi
echo "-----------------Dependency Checks PASSED------------------"

######################################################################
## Install dependencies for 
######################################################################
if ! pip3 install -r requirements.txt
then
    echo "**** ERROR: Python dependency install failed. Cannot continue."
fi
echo "-----------------Requirements Installation PASSED------------------"


######################################################################
## Generate the DB file
######################################################################
echo "--------------------Generating DB file---------------------"
cd aca_db
if [[ -f $aca_sql_file ]]; then

    ## if a file exist it will remove before generating a new file
    if [[ -f $aca_db_file ]]; then
        rm $aca_db_file
    fi

    cat $aca_sql_file | sqlite3 $aca_db_file
else
    echo "**** ERROR: aca_db/$aca_sql_file file does not exist. Cannot continue."
    exit 1
fi
cd ..
echo "--------------------Generated DB file----------------------"





######################################################################
## Generating KG Utility Files
######################################################################
echo "--------------Generating KG Utility Files------------------"
if [ ! -d "aca_backend_api/ontologies/" ]; then
    echo "creating ontologies dir"
    mkdir aca_backend_api/ontologies/

elif [ -d "aca_backend_api/ontologies/" ]; then
    echo "--------Folder exists.-------------------------------------"

else
    echo "**** ERROR: Folder cannot be created. Cannot continue."
    exit 1
fi

## make sure you check the config.ini file
if [ -e aca_backend_api/ontologies/class_type_mapper.json ]; then
    echo "-------------Files exists.---------------------------------"
else
    cd aca_kg_utils
    python kg_utils.py
    cd ..
    echo "----------------Generated KG Utility Files--------------------"
fi


######################################################################
## Generating Entity Standardizer Models
######################################################################
echo "--------Generating Entity Standardizer Models--------------"
if [ ! -d "aca_backend_api/model_objects/" ]; then
    echo "creating model objects dir"
    mkdir aca_backend_api/model_objects/
elif [ -d "aca_backend_api/model_objects/" ]; then
    echo "--------Folder exists.-------------------------------------"
else
    echo "**** ERROR: Folder cannot be created. Cannot continue."
    exit 1
fi

## make sure you check the config.ini file
if [ -e aca_backend_api/model_objects/standardization_dict.pickle -a  -e aca_backend_api/model_objects/standardization_model.pickle -a  -e aca_backend_api/model_objects/standardization_vectorizer.pickle ]; then
    echo "-------------Files exists.---------------------------------"
else
    cd aca_entity_standardizer
    python model_builder.py
    cd ..
    echo "---------Generated Entity Standardizer Models--------------"
fi

echo "+---------------------------------------------------------+"
echo "|-Set up for Tackle Containerzation Adviser Completed !!!-|"
echo "+---------------------------------------------------------+"
