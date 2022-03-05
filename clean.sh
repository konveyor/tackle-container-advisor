#!/bin/bash

aca_db_file="aca_kg_ce_1.0.3.db"
echo "-----------Cleaning Files and Folders---------"

##remove files from backend api
if [ -d "aca_backend_api/model_objects" ]; then
    rm -rf aca_backend_api/model_objects
fi

#remove files from ontologies
if [ -d aca_backend_api/ontologies/ ]; then
    rm  -rf aca_backend_api/ontologies/
fi

## remove db file from DB
if [[ -f aca_db/$aca_db_file ]]; then
    rm aca_db/$aca_db_file
fi


echo "-----------Cleaning Completed---------"
