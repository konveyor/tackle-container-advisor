#!/bin/bash

######################################################################
######################################################################
##     SETUP SCRIPT FOR TACKLE CONTAINER ADVISOR ENVIRONMENT
######################################################################
######################################################################

echo "+---------------------------------------------------------+"
echo "|---------Setting up Tackle Containerzation Adviser-------|"
echo "+---------------------------------------------------------+"
version="1.0.4"
sql_file="$version.sql"
db_file="$version.db"

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
    python -m pip install --upgrade pip wheel build setuptools
fi

# Check to make sure pip3 is installed
if ! command -v pip3 &> /dev/null
then
    echo "**** ERROR: pip3 command could not be found. Cannot continue."
    exit 1
else
    pip3 install setuptools==59.6.0
fi
echo "-----------------Dependency Checks PASSED------------------"

######################################################################
## Install dependencies for 
######################################################################
echo "------------------Installing requirements--------------------"
pip3 install -r entity_standardizer/requirements.txt
if [ $? -ne 0 ]; then
    echo "**** ERROR: Failed to install entity_standardizer dependencies. Cannot continue."
fi

cd entity_standardizer
python -m build
if [ $? -ne 0 ]; then
    echo "**** ERROR: Failed to build entity_standardizer package. Cannot continue."
    exit 1
fi

pip3 install dist/entity_standardizer_tca-1.0-py3-none-any.whl
if [ $? -ne 0 ]; then
    echo "**** ERROR: Failed to install entity_standardizer package. Cannot continue."
    exit 1
else
    cd ..
fi

pip3 install -r service/requirements.txt
if [ $? -ne 0 ]; then
    echo "**** ERROR: Failed to install service dependencies. Cannot continue."
    exit 1
fi

echo "-----------------Requirements Installation PASSED------------------"


######################################################################
## Generate the DB file
######################################################################
echo "--------------------Generating DB file---------------------"
cd db
if [[ -f $sql_file ]]; then

    ## if a file exist it will remove before generating a new file
    if [[ -f $db_file ]]; then
        rm $db_file
    fi

    cat $sql_file | sqlite3 $db_file
else
    echo "**** ERROR: db/$sql_file file does not exist. Cannot continue."
    exit 1
fi
cd ..
echo "--------------------Generated DB file----------------------"

######################################################################
## Generating KG Utility Files
######################################################################
echo "--------------Generating KG Utility Files------------------"
python kg_utils/generator.py
python kg_utils/kg_utils.py
echo "----------------Generated KG Utility Files--------------------"

######################################################################
## Generating Entity Standardizer Models
######################################################################
echo "--------------Generating Entity Standardizer Models------------------"
python benchmarks/generate_data.py
wget https://ibm.box.com/shared/static/mnp323fxslbel8qjecfmryvs8yypooka.pt -O "./models/deploy/siamese.pt"
python benchmarks/run_models.py
echo "---------Generated Entity Standardizer Models--------------"

echo "+---------------------------------------------------------+"
echo "|-Set up for Tackle Containerization Adviser Completed !!!-|"
echo "+---------------------------------------------------------+"
