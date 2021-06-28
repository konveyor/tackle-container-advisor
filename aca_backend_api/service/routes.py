# *****************************************************************
# Copyright IBM Corporation 2021
# Licensed under the Eclipse Public License 2.0, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# *****************************************************************

import logging
from flask import Flask, jsonify, redirect, url_for, request
from flask_restplus import Api, Resource, fields, reqparse, inputs
from werkzeug.middleware.proxy_fix import ProxyFix


import os
from . import app
import planner

import configparser

config = configparser.ConfigParser()
config.read('config.ini')
print('config',config.sections())

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'accesstoken'
    }
}

auth_headers = {'Accept' : 'application/json', 'Content-Type' : 'application/json'}
auth_url = None
if 'RBAC_auth_url' in config['RBAC']:
    auth_url = '{}/api/v2/access?client=api&action_name=rpt%3Aview-analytics'.format(config['RBAC']['RBAC_auth_url'])
logging.warn(f'auth_url: {auth_url}')


app.wsgi_app = ProxyFix(app.wsgi_app)

######################################################################
# Configure Swagger before initilaizing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Application Containerization Advisor API',
          description='These are the REST calls you can make to the ACA to get assessment details.',
          default='Containerization',
          default_label='Containerization Assessment',
          doc='/', # default also could use doc='/apidocs/'
          authorizations=authorizations,
          # prefix='/api'
         )

input_model = api.model('Input', {
    "application_name": fields.String(required=True, description='Name of the application'),
    "application_description": fields.String(required=False, description='Description of the application'),
    "component_name": fields.String(required=False, description='Component/Deployment Unit of the application'),
    "operating_system": fields.String(required=False, description='Operating System of the application'),
    "programming_languages": fields.String(required=False, description='Programming Language of the application'),
    "middleware": fields.String(required=False, description='Middleware used in the application'),
    "database": fields.String(required=False, description='Database used in the application'),
    "integration_services_and_additional_softwares": fields.String(required=False, description='Integration Services and additional software'),
    "technology_summary": fields.String(required=False, description='Additional technology information for the application')
    })


assessment_model = api.model('Assessment', {
    "Name": fields.String(required=True, description='Name of the application'),
    "Desc": fields.String(required=True, description='Description of the application'),
    "Cmpt": fields.String(required=True, description='Component/Deployment Unit of the application'),
    "OS": fields.String(required=False, description='Operating system'),
    "Lang": fields.String(required=False, description='Programming language'),
    "App Server": fields.String(required=False, description='Application server'),
    "Dependent Apps": fields.String(required=False, description='Database and software'),
    "Libs": fields.String(required=False, description='Additional libraries'),
    "Reason": fields.String(required=False, description='Reason for assessment'),
    "KG Version": fields.String(required=False, description='KG Version')
    # "Tech Confidence": fields.String(required=False, description='Technology assessment confidence level')
    })


output_model = api.model('Output', {
    "status": fields.Integer(required=True, description='Status of the call'),
    "message": fields.String(required=True, description='Status message'),
    'assessment': fields.List(fields.Nested(assessment_model), required=True, description='An array of containerization assessment for application workload')
    })


@api.route('/containerization-assessment', strict_slashes=False)
class ContainerizationAssessment(Resource):
    """
    ContainerizationAssessment class creates the assessment in the form of assessment_model for the
    application/component details given in the input_model
    """
    @api.doc('create_containerization_assessment')
    @api.response(201, 'Assessment Completed successfully!')
    @api.response(400, 'Input data format doesn\'t match the format expected by ACA')
    @api.response(401, 'Unauthorized, missing or invalid access token')
    @api.response(500, 'Internal Server Error, missing or wrong config of RBAC access token validation url')
    @api.expect([input_model])
    @api.marshal_with(output_model)
    @api.doc(security='apikey')


    def post(self):
        """
        Invoke do_assessment method in assessment class to initiate assessment process
        """
        return planner.do_plan(auth_url,dict(request.headers),auth_headers,api.payload)

@api.route('/health_check')
@api.response(200, 'HTTP OK')
@api.response(400, 'HTTP Bad Request')
@api.response(500, 'HTTP Internal Server Error')
class HealthCheck(Resource):
    def get(self):
        """
        Healthcheck api is monitor all the api requests and responses. Terminate the service if any issue encountered in
        api request processing
        """
        return 'RUNNING'
