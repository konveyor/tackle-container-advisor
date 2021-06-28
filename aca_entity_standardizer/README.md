


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

	
