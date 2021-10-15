## TCA's Entity Standardizer


### Create conda virtual environment
	# Requires python 3.8
	conda create --name <env-name> python=3.8
	conda activate <env-name>
### Clone Tackle Containerization Adviser 
	git clone git@github.ibm.com:tackle/tackle-advise-containerization.git

### ACA entity standardizer

Python scripts to generate entity standardization model

### How to use

- ``cd tackle-advise-containerization/aca_entity_standardizer``
- ``pip3 install -r requirements.txt``


### Input data from
 ``aca_db`` 
 
### For configuration see 
 ``config.ini``
### Run the following to build the model
 ``python model_builder.py``
### Output saved in 
  ``model``

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

### For testing different use cases
-``python sim_standardizer_tester.py``

### For generating zero shot and few shot benchmarks
- ``python benchmarks.py``

### For running zero shot and few shot baselines
- ``python run_tests.py``

### History of Basline runs
<details>
  <summary>List of baseline runs after PR merges</summary>
  
  ## PR [#68](https://github.com/konveyor/tackle-container-advisor/pull/68)
	 Entities: 447 entities have qids.
     Mentions: 6285 collected, 163 no external link, 384 no qid, 0 empty, 634 duplicates, 629 conflicts.
     Samples:  4110 train, 2175 test.
	 
	 |Method|top-1|top-3|top-5|top-10|top-inf(count)|
     |------|-----|-----|-----|------|--------------|
     |WD api|0.39 |0.53 |0.59 |0.61  |0.68 (1470)   |
     |TFIDF |0.00 |0.00 |0.00 |0.00  |0.00 (1)      |

</details>
  


	
