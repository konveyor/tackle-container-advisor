# Running TCA
[Back to main page](https://github.com/konveyor/tackle-container-advisor#table-of-contents)
## Table of Contents
1. [Running TCA as a service](#Running-TCA-as-a-service)
2. [Running TCA as a cli](#Running-TCA-as-a-cli)
3. [Running performance tests](#Run-a-performance-test-for-TCA-service)
4. [Running TCA with a new version of Knowledge Base](#Running-TCA-with-a-new-version-of-Knowledge-Base)

## Setting up your environment

Requires Python >= 3.6 environment. You cannot run this code without having a proper
Python environment first. We recommend that you follow the instructions
in the [Developer's Guide](docs/development.md) before proceeding further.


## Running TCA as a service

There are 4 options for deploying TCA as a service.

1. Install the service requirements and start the service from command line.

Requires *gunicorn* standalone installation on your system.
```
bash setup.sh
gunicorn --workers=2 --threads=500 --timeout 300 service:app
OR
waitress-serve --listen=*:8000 service:app
```

2. Running the service as a container.

Using a bash script.
```
bash run.sh
```
Using command line.
```
docker-compose  -f 'docker-compose-api.yml' up -d --build
```

3. Running the service in a virtual machine using vagrant.
```
vagrant up
vagrant ssh
cd /vagrant
bash run.sh
```

4. Deploy the container on Redhat Openshift Container Platform.

```
bash deploy.sh
```
## Running TCA as a cli

TCA application can be invoked from the command-line as follows:
```
usage: tca_cli.py [-h] -input_json INPUT_JSON -operation OPERATION -catalog CATALOG -output_json OUTPUT_JSON


optional arguments:
  -h, --help     show this help message and exit
  -input_json INPUT_JSON  input to the application in json format
  -operation OPERATION    operation to perform: standardize (default)| containerize
  -catalog CATALOG  catalog: dockerhub (defailt) | openshift | operator
  -output_json OUTPUT_JSON  output from the application in json format
```

## Run a performance test for TCA service
A performance test measures the response time of TCA service under
various load conditions. Before running
performance test, update *config/test.ini* with the hostname
and port where TCA service has been deployed

```
python test/performance/run_payload.py <#users> <#applications/user>
```

### Performance Benchmarking

- TCA Api was run as a podman container on IntelCore i9-10885H CPU @ 2.40GHz with 8 Cores, 16 Logical Processors with 4GB Memory limit
	
<table>
  <tr>
    <td> #Records </td>
    <td> Avg. Response Time </td>
    <td> Server Peak Mem.   </td>
    <td> Network I/O        </td>	  
  </tr>
  <tr>	
    <td> 10 </td>
    <td> 4.7s </td>
    <td> 477.1MB / 4.194GB </td>
    <td> 10.57kB / 8.129kB </td>
  </tr>
  <tr>	
    <td> 100 </td>
    <td> 13.73s </td>
    <td> 470.5MB / 4.194GB </td>
    <td> 81.78kB / 50.87kB </td>
  </tr>
  <tr>	
    <td> 1000 </td>
    <td> 42.75s </td>
    <td> 446.8MB / 4.194GB </td>
    <td> 644.3kB / 377.4kB </td>
  </tr>
  <tr>	
    <td> 5000 </td>
    <td> 226.29s </td>
    <td> 497.8MB / 4.194GB </td>
    <td> 3.814MB / 2.375MB </td>
  </tr>
</table>


## Running TCA with a new version of Knowledge Base

Please perform the following steps.

1. Replace the existing .sql file with the new <new_db>.sql file in the db folder

2. Change the *common.ini* file in the config folder as follows

    version = <new_db>

3. Modify the *setup.sh* and *clean.sh* scripts to reflect the version accordingly.

    version=<new_db>

4. Re-run *setup.sh* and then deploy the service.
