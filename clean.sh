#!/bin/bash

version="1.0.3"
db_file="$version.db"
echo "-----------Cleaning Files and Folders---------"

##remove files from backend api
if [ -d models/ ]; then
    rm -rf models/
fi

#remove files from ontologies
if [ -d kg/ ]; then
    rm  -rf kg/
fi

## remove db file from DB
if [[ -f db/$db_file ]]; then
    rm db/$db_file
fi


echo "-----------Cleaning Completed---------"
