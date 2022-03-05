## TCA's Entity Standardizer


### Create conda virtual environment
	# Requires python 3.8
	conda create --name <env-name> python=3.8
	conda activate <env-name>
### Clone Tackle Containerization Adviser 
	git clone it clone git@github.com:konveyor/tackle-container-advisor.git

### TCA entity standardizer

Python scripts to generate entity standardization model

### How to use

- ``cd tackle-container-advisor``
- ``pip3 install -r requirements.txt``
- ``cd aca_entity_standardizer``


### Input data from
 ``aca_db`` 
 
### For configuration see 
 ``config.ini``
### Run the following to build the model
 ``python model_builder.py``
### Output saved in 
  ``model_path`` from ``config.ini``

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
  
### 2021-10-19 ([View diff](https://github.com/konveyor/tackle-container-advisor/commit/c51e6bf4e0fbf27acb6a8f4998274b48549dfc41))
1. Entities: 447 entities have qids.
2. Mentions: 6285 collected, 163 no external link, 384 no qid, 0 empty, 634 duplicates, 629 conflicts.
3. Samples:  4110 train, 2175 test.
WD api with no ctx took 1870.15 seconds.
TFIDF model took 40.27 seconds.
<p><table>
<thead>
<tr><th>Method</th><th>top-1</th><th>top-3</th><th>top-5</th><th>top-10</th><th>top-inf(count)</th></tr>
</thead>
<tbody>
<tr><td>WD api</td><td>0.39</td><td>0.53</td><td>0.59</td><td>0.61</td><td>0.68 (1470)</td></tr>
<tr><td>TFIDF</td><td>0.71</td><td>0.71</td><td>0.71</td><td>0.71</td><td>0.71 (1550)</td></tr>
</tbody>
</table></p>		
</details>	
