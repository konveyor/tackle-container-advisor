# APIs
[Back to main page](https://github.com/konveyor/tackle-container-advisor#table-of-contents)

The following are the different APIs in TCA
1. [Standardize](#Standardize)
2. [Containerize](#Containerize)
3. [Clustering](#Clustering)

### [Example Requests and Responses](https://divsan93.github.io/)

## Standardize
The given application description (raw input from client) is standardized and matching entities and versions are extracted from the knowledge graph

### Response format to a post request /standardize:
You can make RESTful calls to TCA to assess details of your application workload. As a first step, the standardize api standardizes the natural language input provided by a client.It accepts a `POST` request and a `json` payload. Following is the input data format and the output response format.


#### Input Format:

```
[
  {
    "application_name": "string",
    "application_description": "string",
    "technology_summary": "string"
  }
]
```

Example input:
```
[
{
  "application_name": "App1",
  "application_description": "application",
  "technology_summary": "rhel,java,db2"
}
]
```

### Response format to a post request /standardize:
Following is the `json` response format to a `post /standardize` request.

Output format:
```
{
  "status": 0,
  "message": "string",
  "standardized_apps": [
    {
      "Name": "string",
      "Desc": "string",
      "Cmpt": "string",
      "OS": "string",
      "Lang": "string",
      "App Server": "string",
      "Dependent Apps": "string",
      "Runtime": "string",
      "Libs": "string",
      "Reason": "string",
      "KG Version": "string"
    }
  ]
}
```

Example output:
```
{
  "status": 201,
  "message": "Standardization completed successfully!",
  "standardized_apps": [
    {
      "Name": "App1",
      "Desc": "application",
      "Cmpt": "",
      "OS": "{'rhel': {'Linux|Red Hat Enterprise Linux': ('NA_VERSION', '8.3')}}",
      "Lang": "{'java': {'Java|*': ('NA_VERSION', '21')}}",
      "App Server": "{}",
      "Dependent Apps": "{'db2': {'DB2': ('NA_VERSION', '11.5')}}",
      "Runtime": "{}",
      "Libs": "{}",
      "Reason": "",
      "KG Version": "1.0.4"
    }
  ]
}
```

## Containerize
The standardized output from the above step is taken and matched with the container image information in the knowledge base to generate  recommendations. Image recommendations come with a confidence score, based on match accuracy.

### Response format to a post request /containerization:
Please note that the standardized output act as containerization input
Following is the `json` response format to a `post /containerization` request.

Payload output format:
```
{
  "status": 0,
  "message": "string",
  "clusters": [
    {
      "id": 0,
      "name": "string",
      "type": "string",
      "tech_stack": [
        "string"
      ],
      "num_elements": 0,
      "apps": [
        {
          "Name": "string",
          "Desc": "string",
          "Cmpt": "string",
          "OS": "string",
          "Lang": "string",
          "App Server": "string",
          "Dependent Apps": "string",
          "Runtime": "string",
          "Libs": "string",
          "Reason": "string",
          "KG Version": "string"
        }
      ]
    }
  ]
}
```

Example output:
```
{
  "status": 201,
  "message": "Container recommendation generated!",
  "containerization": [
    {
      "Name": "App1",
      "Desc": "application",
      "Cmpt": "",
      "Valid": true,
      "Ref Dockers": "1. {'db2(Verified Publisher)': 'https://hub.docker.com/r/ibmcom/db2'}",
      "Confidence": 0.86,
      "Reason": "Additional Installations in container image 1: Java|*",
      "Recommend": "Containerize"
    }
  ]
}
```

## Clustering
The standardized output from the Standardize step is taken and used to group together applications with an equivalent technology stack into clusters. For each cluster, the api returns the shared technology stack description, the number of applications in it, and their details.

### Response format to a post request /clustering:
Please note that the above standardized output act as the input to clustering
Following is the `json` response format to a `post /clustering` request.

Payload input format:
```
[
  {
    "Name": "string",
    "Desc": "string",
    "Cmpt": "string",
    "OS": "string",
    "Lang": "string",
    "App Server": "string",
    "Dependent Apps": "string",
    "Runtime": "string",
    "Libs": "string",
    "Reason": "string",
    "KG Version": "string"
  }
]

```
Example input:
```
[
  {"Name": "App 1",
   "Desc": "",
   "Cmpt": "Component 1",
   "OS": "{'ZOS': {'MVS|z/OS': ('NA_VERSION', 'NA_VERSION')}}",
   "Lang": "{'JavaScript': {'JavaScript|*': ('NA_VERSION', 'ES6')}, 'PL/1': {'PL/I': ('1', '1')}}",
   "App Server": "{}",
   "Dependent Apps": "{}",
   "Runtime": "{}",
   "Libs": "{}",
   "Reason": "",
   "KG Version": "1.0.4"},
  {"Name": "App 2",
   "Desc": "",
   "Cmpt": "Component 1",
   "OS": "{'Windows 2016 Standard': {'Windows|Windows Server': ('2016 standard', '2016 standard')}}",
   "Lang": "{'JavaScript': {'JavaScript|*': ('NA_VERSION', 'ES6')}}",
   "App Server": "{}",
   "Dependent Apps": "{}",
   "Runtime": "{}",
   "Libs": "{}",
   "Reason": "",
   "KG Version": "1.0.4"},
  {"Name": "App 3",
   "Desc": "",
   "Cmpt": "Component 1",
   "OS": "{'Windows': {'Windows|*': ('NA_VERSION', 'NA_VERSION')}}",
   "Lang": "{'C#': {'C#': ('NA_VERSION', 'NA_VERSION')}}",
   "App Server": "{}",
   "Dependent Apps": "{}",
   "Runtime": "{'ASP.net': {'Active Server Pages (ASP)': ('NA_VERSION', '3')}}",
   "Libs": "{}",
   "Reason": "",
   "KG Version": "1.0.4"},
  {"Name": "App 4",
   "Desc": "",
   "Cmpt": "Component 1",
   "OS": "{'AIX': {'Unix|AIX': ('NA_VERSION', 'NA_VERSION')}, 'zOS': {'MVS|z/OS': ('NA_VERSION', 'NA_VERSION')}}",
   "Lang": "{'Java': {'Java|*': ('NA_VERSION', 'NA_VERSION')}}",
   "App Server": "{}",
   "Dependent Apps": "{}",
   "Runtime": "{}",
   "Libs": "{}",
   "Reason": "",
   "KG Version": "1.0.4"},
  {"Name": "App 5",
   "Desc": "",
   "Cmpt": "Component 1",
   "OS": "{'zOS': {'MVS|z/OS': ('NA_VERSION', 'NA_VERSION')}}",
   "Lang": "{'JavaScript': {'JavaScript|*': ('NA_VERSION', 'ES6')}, 'PL1': {'PL/I': ('1', '1')}}",
   "App Server": "{}",
   "Dependent Apps": "{}",
   "Runtime": "{}",
   "Libs": "{}",
   "Reason": "",
   "KG Version": "1.0.4"}
]

```
Example output:
```
{
  "status": 201,
  "message": "Clustering completed successfully!",
  "clusters": [
    {
      "id": 0,
      "name": "unique_tech_stack_0",
      "type": "unique",
      "tech_stack": [
        "PL/I",
        "MVS|*",
        "JavaScript|*"
      ],
      "num_elements": 2,
      "apps": [
        {
          "Name": "App 1",
          "Desc": "",
          "Cmpt": "Component 1",
          "OS": "{'ZOS': {'MVS|z/OS': ('NA_VERSION', 'NA_VERSION')}}",
          "Lang": "{'JavaScript': {'JavaScript|*': ('NA_VERSION', 'ES6')}, 'PL/1': {'PL/I': ('1', '1')}}",
          "App Server": "{}",
          "Dependent Apps": "{}",
          "Runtime": "{}",
          "Libs": "{}",
          "Reason": "",
          "KG Version": "1.0.4"
        },
        {
          "Name": "App 5",
          "Desc": "",
          "Cmpt": "Component 1",
          "OS": "{'zOS': {'MVS|z/OS': ('NA_VERSION', 'NA_VERSION')}}",
          "Lang": "{'JavaScript': {'JavaScript|*': ('NA_VERSION', 'ES6')}, 'PL1': {'PL/I': ('1', '1')}}",
          "App Server": "{}",
          "Dependent Apps": "{}",
          "Runtime": "{}",
          "Libs": "{}",
          "Reason": "",
          "KG Version": "1.0.4"
        }
      ]
    },
    {
      "id": 1,
      "name": "unique_tech_stack_1",
      "type": "unique",
      "tech_stack": [
        "MVS|*",
        "Unix|*",
        "Java|*"
      ],
      "num_elements": 1,
      "apps": [
        {
          "Name": "App 4",
          "Desc": "",
          "Cmpt": "Component 1",
          "OS": "{'AIX': {'Unix|AIX': ('NA_VERSION', 'NA_VERSION')}, 'zOS': {'MVS|z/OS': ('NA_VERSION', 'NA_VERSION')}}",
          "Lang": "{'Java': {'Java|*': ('NA_VERSION', 'NA_VERSION')}}",
          "App Server": "{}",
          "Dependent Apps": "{}",
          "Runtime": "{}",
          "Libs": "{}",
          "Reason": "",
          "KG Version": "1.0.4"
        }
      ]
    },
    {
      "id": 2,
      "name": "unique_tech_stack_2",
      "type": "unique",
      "tech_stack": [
        "Windows|*",
        "C#",
        "Active Server Pages (ASP)"
      ],
      "num_elements": 1,
      "apps": [
        {
          "Name": "App 3",
          "Desc": "",
          "Cmpt": "Component 1",
          "OS": "{'Windows': {'Windows|*': ('NA_VERSION', 'NA_VERSION')}}",
          "Lang": "{'C#': {'C#': ('NA_VERSION', 'NA_VERSION')}}",
          "App Server": "{}",
          "Dependent Apps": "{}",
          "Runtime": "{'ASP.net': {'Active Server Pages (ASP)': ('NA_VERSION', '3')}}",
          "Libs": "{}",
          "Reason": "",
          "KG Version": "1.0.4"
        }
      ]
    },
    {
      "id": 3,
      "name": "unique_tech_stack_3",
      "type": "unique",
      "tech_stack": [
        "Windows|*",
        "JavaScript|*"
      ],
      "num_elements": 1,
      "apps": [
        {
          "Name": "App 2",
          "Desc": "",
          "Cmpt": "Component 1",
          "OS": "{'Windows 2016 Standard': {'Windows|Windows Server': ('2016 standard', '2016 standard')}}",
          "Lang": "{'JavaScript': {'JavaScript|*': ('NA_VERSION', 'ES6')}}",
          "App Server": "{}",
          "Dependent Apps": "{}",
          "Runtime": "{}",
          "Libs": "{}",
          "Reason": "",
          "KG Version": "1.0.4"
        }
      ]
    }
  ]
}
```
