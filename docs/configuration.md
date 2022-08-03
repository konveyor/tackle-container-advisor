---
layout: default
title: Configuration
nav_order: 2
---
## Configuration

This folder contains config files for various packages. 

* ``common.ini`` contains configuration data that is common to all packages. 
* ``kg.ini`` contains configuration data used to generate json files from the knowledge
base (sql and db) files. These json files contain all the knowledge base data that is 
needed by various packages.    
* The ``tca`` and ``wikidata`` are folders corresponding to two tasks that are created by 
``benchmarks/generate_data.py``. The ``tfidf`` entity standardization approach runs on the
``tca`` task and ``wdpapi`` entity standardization approach runs on the ``wikidata`` task. 
The configuration data for each approach can be found in the respective task directories.
