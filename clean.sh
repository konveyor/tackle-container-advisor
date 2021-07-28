#!/bin/bash

aca_db_file="aca_kg_ce_1.0.0.db"
echo "-----------Cleaning Files and Folders---------"

##remove files from backend api
if [ -d "aca_backend_api/model_objects" ]; then
    rm -rf aca_backend_api/model_objects
fi

#remove files from ontologies
if [ -d aca_backend_api/ontologies/ ]; then
    rm  -rf aca_backend_api/ontologies/
fi

## remove db file from DB, kg_utils, and entity_standardizer
if [[ -f aca_db/$aca_db_file ]]; then
    rm aca_db/$aca_db_file
fi

if [ -d "aca_kg_utils/aca_db" ]; then
    rm -rf aca_kg_utils/aca_db
fi

if [ -d "aca_entity_standardizer/aca_db" ]; then
    rm -rf aca_entity_standardizer/aca_db
fi

## remove models
if [ -d "aca_entity_standardizer/model_objects" ]; then
    rm -rf aca_entity_standardizer/model_objects
fi

## remove kg utilities
if [ -d "aca_kg_utils/ontologies" ]; then
    rm -rf aca_kg_utils/ontologies
fi

echo "-----------Cleaning Completed---------"
