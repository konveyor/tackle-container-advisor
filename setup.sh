#!/bin/bash

echo "-----------Setting up Tackle Containerzation Adviser---------"
aca_sql_file="aca_kg_ce_1.0.1.sql"
aca_db_file="aca_kg_ce_1.0.1.db"

##generate the DB file
echo "-----------Generating DB file--------------------------------"
cd aca_db
if [[ -f $aca_sql_file ]]; then
    
    ## if a file exist it will remove before generating a new file
    if [[ -f $aca_db_file ]]; then
        rm $aca_db_file
    fi
        
    cat $aca_sql_file | sqlite3 $aca_db_file
else
    echo "-----------File does not exist. Please check with Admins."
    exit 0
fi
echo "-----------Generated DB file---------------------------------"


##copy DB file to the entity standardization module
echo "-----------Copying DB file to Entity Standardization Module--"
cd ..
if [ ! -d "aca_entity_standardizer/aca_db/" ]; then
    mkdir aca_entity_standardizer/aca_db/

elif [ -d "aca_entity_standardizer/aca_db/" ]; then
    echo "-----------Folder exists.--------------------------------"
    
else
    echo "---Folder cannot be created. Please check with Admins.---"
    exit 0
fi

cp aca_db/$aca_db_file aca_entity_standardizer/aca_db/.
echo "-----------Copied DB file to Entity Standardization Module-----"

##copy the DB file to the KG util module

echo "-----------Copying DB file to The KG Utility-------------------"
if [ ! -d "aca_kg_utils/aca_db/" ]; then
    mkdir aca_kg_utils/aca_db/
    
elif [ -d "aca_kg_utils/aca_db/" ]; then
    echo "-----------Folder exists.----------------------------------"
    
else
    echo "-----Folder cannot be created. Please check with Admins.---"
    exit 0
fi
cp aca_db/$aca_db_file aca_kg_utils/aca_db/.
    
echo "-----------Copied DB file to KG Utility------------------------"


echo "-----------Generating KG Utility Files ------------------------"

if [ ! -d "aca_kg_utils/ontologies/" ]; then
    echo "creating ontologies dir"
    mkdir aca_kg_utils/ontologies/
    
elif [ -d "aca_kg_utils/ontologies/" ]; then
    echo "-----------Folder exists.----------------------------------"
    
else
    echo "-----------Folder cannot be created. Please check with Admins.---"
    exit 0
fi

## make sure you check the config.ini file
if [ -e aca_kg_utils/ontologies/class_type_mapper.json ]; then
    echo "-------------------Files exist.----------------------------------"
else
    cd aca_kg_utils
    pip3 install -r requirements.txt
    python kg_utils.py
    cd ..
    echo "-----------Generated KG Utility Files ------------------------"
fi

echo "-----------Copying KG Utility Files to Backend API------------------------"
if [ -d "aca_backend_api/ontologies/" ]; then
    cp aca_kg_utils/ontologies/*.json aca_backend_api/ontologies/.
else
    echo "-----------Folder does not exist. Please check with Admins.---"
    exit 0
fi
echo "-----------Copied KG Utility Files to Backend API------------------------"


echo "-----------Generating Entity Standardizer Models------------------------"
if [ ! -d "aca_entity_standardizer/model_objects/" ]; then
    echo "creating model objects dir"
    mkdir aca_entity_standardizer/model_objects/
elif [ -d "aca_entity_standardizer/model_objects/" ]; then
    echo "-----------Folder exists.----------------------------------"
else
    echo "-----------Folder cannot be created. Please check with Admins.---"
    exit 0
fi
## make sure you check the config.ini file
if [ -e aca_entity_standardizer/model_objects/standardization_dict.pickle -a  -e aca_entity_standardizer/model_objects/standardization_model.pickle -a  -e aca_entity_standardizer/model_objects/standardization_vectorizer.pickle ]; then
    echo "-------------------Files exist.----------------------------------"
else
    cd aca_entity_standardizer
    pip3 install -r requirements.txt
    python model_builder.py
    cd ..
    echo "-----------Generated Entity Standardizer Models ------------------------"
fi
    
echo "-----------Copying Entity Standardizer Models to Backend API------------------------"
if [ ! -d  "aca_backend_api/model_objects/" ]; then
    mkdir aca_backend_api/model_objects/

elif [ -d  "aca_backend_api/model_objects/" ]; then
    echo "-----------Folder exists.----------------------------------"
else
    echo "-----------Folder cannot be created. Please check with Admins.---"
    exit 0
fi
cp aca_entity_standardizer/model_objects/*.pickle aca_backend_api/model_objects/.
echo "-----------Copying Entity Standardizer Models to Backend API------------------------"

echo "-----------Set up for Tackle Containerzation Adviser Completed !!!---------"
