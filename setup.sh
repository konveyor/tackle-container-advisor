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
## Copy DB file to the entity standardization module
######################################################################
echo "-----Copying DB file to Entity Standardization Module------"
if [ ! -d "aca_entity_standardizer/aca_db/" ]; then
    mkdir aca_entity_standardizer/aca_db/

elif [ -d "aca_entity_standardizer/aca_db/" ]; then
    echo "--------Folder exists.-------------------------------------"

else
    echo "**** ERROR: Folder cannot be created. Cannot continue."
    exit 1
fi

cp aca_db/$aca_db_file aca_entity_standardizer/aca_db/.
echo "------Copied DB file to Entity Standardization Module------"


######################################################################
## Copy the DB file to the KG util module
######################################################################
echo "-----------Copying DB file to The KG Utility---------------"
if [ ! -d "aca_kg_utils/aca_db/" ]; then
    mkdir aca_kg_utils/aca_db/

elif [ -d "aca_kg_utils/aca_db/" ]; then
    echo "--------Folder exists.-------------------------------------"

else
    echo "**** ERROR: Folder cannot be created. Cannot continue."
    exit 1
fi
cp aca_db/$aca_db_file aca_kg_utils/aca_db/.
echo "--------------Copied DB file to KG Utility-----------------"


######################################################################
## Generating KG Utility Files
######################################################################
echo "--------------Generating KG Utility Files------------------"
if [ ! -d "aca_kg_utils/ontologies/" ]; then
    echo "creating ontologies dir"
    mkdir aca_kg_utils/ontologies/

elif [ -d "aca_kg_utils/ontologies/" ]; then
    echo "--------Folder exists.-------------------------------------"

else
    echo "**** ERROR: Folder cannot be created. Cannot continue."
    exit 1
fi

## make sure you check the config.ini file
if [ -e aca_kg_utils/ontologies/class_type_mapper.json ]; then
    echo "-------------Files exists.---------------------------------"
else
    cd aca_kg_utils
    if ! pip3 install -r requirements.txt; then
        echo "**** ERROR: Python dependency install failed. Cannot continue."
        exit 1
    fi
    python kg_utils.py
    cd ..
    echo "----------------Generated KG Utility Files--------------------"
fi


######################################################################
## Copying KG Utility Files to Backend API
######################################################################
echo "--------Copying KG Utility Files to Backend API------------"
if [ -d "aca_backend_api/ontologies/" ]; then
    cp aca_kg_utils/ontologies/*.json aca_backend_api/ontologies/.
else
    echo "**** ERROR: Folder cannot be created. Cannot continue."
    exit 1
fi
echo "---------Copied KG Utility Files to Backend API------------"


######################################################################
## Generating Entity Standardizer Models
######################################################################
echo "--------Generating Entity Standardizer Models--------------"
if [ ! -d "aca_entity_standardizer/model_objects/" ]; then
    echo "creating model objects dir"
    mkdir aca_entity_standardizer/model_objects/
elif [ -d "aca_entity_standardizer/model_objects/" ]; then
    echo "--------Folder exists.-------------------------------------"
else
    echo "**** ERROR: Folder cannot be created. Cannot continue."
    exit 1
fi

## make sure you check the config.ini file
if [ -e aca_entity_standardizer/model_objects/standardization_dict.pickle -a  -e aca_entity_standardizer/model_objects/standardization_model.pickle -a  -e aca_entity_standardizer/model_objects/standardization_vectorizer.pickle ]; then
    echo "-------------Files exists.---------------------------------"
else
    cd aca_entity_standardizer
    if ! pip3 install -r requirements.txt; then
        echo "**** ERROR: Python dependency install failed. Cannot continue."
        exit 1
    fi
    python model_builder.py
    cd ..
    echo "---------Generated Entity Standardizer Models--------------"
fi

######################################################################
## Copying Entity Standardizer Models to Backend API
######################################################################
echo "-----Copying Entity Standardizer Models to Backend API-----"
if [ ! -d  "aca_backend_api/model_objects/" ]; then
    mkdir aca_backend_api/model_objects/

elif [ -d  "aca_backend_api/model_objects/" ]; then
    echo "--------Folder exists.-------------------------------------"
else
    echo "**** ERROR: Folder cannot be created. Cannot continue."
    exit 1
fi
cp aca_entity_standardizer/model_objects/*.pickle aca_backend_api/model_objects/.
echo "-----Copied Entity Standardizer Models to Backend API------"

echo "+---------------------------------------------------------+"
echo "|-Set up for Tackle Containerzation Adviser Completed !!!-|"
echo "+---------------------------------------------------------+"
