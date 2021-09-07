## Instructions to build the image
In the repo create a config.ini file, add the following flag if not present:

is_disable_access_token=yes

Then run the following to build and run the image
```
docker-compose  -f 'docker-compose-api.yml' up -d --build
```

You can make RESTful calls to the containerization advisor backend service to get assessment details of your application workload. It accepts a `POST` request and a `json` payload. Following is the input data format and the output response format. 


#### Input Format:

```
[
  {
    "application_name": "App 001",
    "application_description": "Description of App 001",
    "component_name": "Component 1",
    "operating_system": "RHEL",
    "programming_languages": ".NET Framework",
    "middleware": "IIS7.5 (ftp)\n.net framewrk 3.x 4.x\nMQ Client 7.5\nRightFax client 10",
    "database": "SqLServer",
    "integration_services_and_additional_softwares": "Tivoli, MQ 7.5",
    "technology_summary": "Windows,.NET/Java: IIS7.5 (ftp)\n.net framewrk 3.x 4.x\nMQ Client 7.5"
  },
  {
    "application_name": "App 002",
    "application_description": "Description of App 002",
    "component_name": "Component 1",
    "operating_system": "Redhat",
    "programming_languages": "Java 8",
    "middleware": "Websphere Application Server",
    "database": "DB2",
    "integration_services_and_additional_softwares": "MQ 7.5",
    "technology_summary": "RightFax client 10"
  }
]
```



### Response format to a post request /containerization-assessment:
Following is the `json` response format given by ACA to a `post /containerization-assessment` request.

```
{
  "status": 201,
  "message": "Assessment completed successfully!",
  "assessment": [
    {
      "Name": "App 001",
      "Desc": "Description of App 001",
      "Cmpt": "Component 1",
      "OS": "{'RHEL': {'Linux|Red Hat Enterprise Linux': ''}}",
      "Lang": "{'Java': {'Java': ''}}",
      "App Server": "{}",
      "Dependent Apps": "{'SqLServer': {'MS SQL Server': ''}, 'MQ 7.5': {'IBM Websphere MQ': '7.5'}}",
      "Runtime": "{}",
      "Libs": "{}",
      "Reason": "Reason 101: Medium or low confidence for the inferred data: {\".net framewrk 3.x 4.x\": {\"Linux|Red Hat Enterprise Linux\": \"3.x 4.x\", \"Websphere Application Server (WAS)\": \"3.x 4.x\", \"Java|Enterprise JavaBeans (EJB)\": \"3.x 4.x\"}, \"MQ Client 7.5\": {\"IBM Websphere MQ\": \"7.5\"}, \"RightFax client 10\": {\"IBM Websphere MQ\": \"10\"}, \"Windows\": {\"Java|IBM SDK\": \"\"}}\nReason 103: Unknown technologies detected: .NET Framework, IIS7.5 (ftp), Tivoli, .NET",
      "KG Version": "1.0.0"
    },
    {
      "Name": "App 002",
      "Desc": "Description of App 002",
      "Cmpt": "Component 1",
      "OS": "{'Redhat': {'Linux|Red Hat Enterprise Linux': ''}}",
      "Lang": "{'Java 8': {'Java': '8'}}",
      "App Server": "{'Websphere Application Server': {'Websphere Application Server (WAS)': ''}}",
      "Dependent Apps": "{'DB2': {'DB2': ''}, 'MQ 7.5': {'IBM Websphere MQ': '7.5'}}",
      "Runtime": "{}",
      "Libs": "{}",
      "Reason": "Reason 101: Medium or low confidence for the inferred data: {\"RightFax client 10\": {\"IBM Websphere MQ\": \"10\"}}",
      "KG Version": "1.0.1"
    }
  ]
}
```

Please note that the above assessment output act as planning input

### Response format to a post request /containerization-planning:
Following is the `json` response format given by ACA to a `post /containerization-planning` request.

```
{
  "status": 201,
  "message": "Planning completed successfully!",
  "planning": [
    {
      "Name": "App 001",
      "Desc": "Description of App 001",
      "Cmpt": "Component 1",
      "Valid": true,
      "Ref Dockers": "1. {'Microsoft SQL Server(Verified Publisher)': 'https://hub.docker.com/_/microsoft-mssql-server'}\n2. {'mq': 'https://hub.docker.com/r/ibmcom/mq/'}",
      "Confidence": 0.89,
      "Reason": "Additional Installations in container image 1,2: Java",
      "Recommend": "Partially Containerize"
    },
    {
      "Name": "App 002",
      "Desc": "Description of App 002",
      "Cmpt": "Component 1",
      "Valid": true,
      "Ref Dockers": "1. {'websphere-traditional': 'https://hub.docker.com/r/ibmcom/websphere-traditional/'}\n2. {'db2': 'https://hub.docker.com/r/ibmcom/db2'}\n3. {'mq': 'https://hub.docker.com/r/ibmcom/mq/'}",
      "Confidence": 1,
      "Reason": "No additonal installations required.",
      "Recommend": "Partially Containerize"
    }
  ]
}
```

## Add Access Token for backend API
We need to config RBAC_auth_url=https://rbac-dev.nextgen-ose-85ee131ed8e71cabc202e5781fab5c58-0000.eu-de.containers.appdomain.cloud in .env file to support access token authorizations. ACA will validate access token to RBAC_auth_url.


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


### For running test cases in a standalone mode.

```
cd aca_backend_api
python -m unittest discover -s test
```