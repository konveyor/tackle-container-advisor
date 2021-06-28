
Python scripts to generate JSON from Database

### Create conda virtual environment
	# Requires python 3.8
	conda create --name <env-name> python=3.8
	conda activate <env-name>
### Clone ACA 
	git clone git@github.ibm.com:tackle/tackle-advise-containerization.git

### How to use
- ``cd tackle-advise-containerization/aca_kg_utils``
- ``pip3 install -r requirements.txt``
- ``aca_db`` provides the input data
- Run ``python kg_utils.py``
- Outputs json are saved in: ``aca_backend_api/ontologies`` and in ``aca_kg_utils/ontologies``
- Latest excel KG is in: ``<https://ibm.ent.box.com/folder/112880079567>``

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
