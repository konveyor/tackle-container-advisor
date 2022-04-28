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
import service.planner as planner

import configparser

config = configparser.ConfigParser()
common = os.path.join("config", "common.ini")
config.read(common)

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
app.logger.warn(f'auth_url: {auth_url}')


app.wsgi_app = ProxyFix(app.wsgi_app)

######################################################################
# Configure Swagger before initilaizing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Tackle Container Advisor (TCA)',
          description='These are the REST calls you can make to the TCA to get assessment and planning details.',
          default='Containerization',
          default_label='Tackle Container Advisor',
          doc='/', # default also could use doc='/apidocs/'
          authorizations=authorizations,
          # prefix='/api'
         )

std_input_model = api.model('Standardizer Input', {
    "tech_mention": fields.String(required=True, description='Usage of technology component')
})

std_output_model = api.model('Standardizer Output', {
    "tech_entity": fields.String(required=True, description='Standardized technology name')
    "tech_entity_type": fields.String(required=True, description='Type of technology entity')
})



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
    "Runtime": fields.String(required=False, description='Runtime'),
    "Libs": fields.String(required=False, description='Additional libraries'),
    "Reason": fields.String(required=False, description='Reason for assessment'),
    "KG Version": fields.String(required=False, description='KG Version')
    })

planning_model = api.model('Planning', {
    "Name": fields.String(required=True, description='Name of the application'),
    "Desc": fields.String(required=True, description='Description of the application'),
    "Cmpt": fields.String(required=True, description='Component/Deployment Unit of the application'),
    "Valid": fields.Boolean(required=True, description='Is the containerization assessment valid?'),
    "Ref Dockers": fields.String(required=False, description='Description of the application'),
    "Confidence": fields.Float(required=False, description='Confidence of the assessment'),
    "Reason": fields.String(required=False, description='Reason for assessment'),
    "Recommend": fields.String(required=False, description='Recommended disposition')
    })


output_model_assessment = api.model('Assessment Output', {
    "status": fields.Integer(required=True, description='Status of the call'),
    "message": fields.String(required=True, description='Status message'),
    'assessment': fields.List(fields.Nested(assessment_model), required=True, description='An array of containerization assessment for application workload')
    })

output_model_planning = api.model('Planning Output', {
    "status": fields.Integer(required=True, description='Status of the call'),
    "message": fields.String(required=True, description='Status message'),
    "containerization": fields.List(fields.Nested(planning_model), required=True, description='An array of containerization assessment for application workload')
    })


@api.route('/entity-standardizer', strict_slashes=False)
class EntityStandardizer(Resource):
    """
    EntityStandardizer class creates the standardization in the form of std_output_model for the
    tech_mentions given in the std_input_model
    """
    @api.doc('create_entity_standardization')
    @api.response(201, 'Stadardization Completed successfully!')
    @api.response(400, 'Input data format doesn\'t match the format expected by TCA')
    @api.response(401, 'Unauthorized, missing or invalid access token')
    @api.response(500, 'Internal Server Error, missing or wrong config of RBAC access token validation url')
    @api.expect([std_input_model])
    @api.marshal_with(std_output_model)
    @api.doc(security='apikey')


    def post(self):
        """
        Invoke do_standardization method in standardization class to initiate stadardization process
        """
        return planner.do_standardization(auth_url,dict(request.headers),auth_headers,api.payload)


@api.route('/containerization-assessment', strict_slashes=False)
class ContainerizationAssessment(Resource):
    """
    ContainerizationAssessment class creates the assessment in the form of assessment_model for the
    application/component details given in the input_model
    """
    @api.doc('create_containerization_assessment')
    @api.response(201, 'Assessment Completed successfully!')
    @api.response(400, 'Input data format doesn\'t match the format expected by TCA')
    @api.response(401, 'Unauthorized, missing or invalid access token')
    @api.response(500, 'Internal Server Error, missing or wrong config of RBAC access token validation url')
    @api.expect([input_model])
    @api.marshal_with(output_model_assessment)
    @api.doc(security='apikey')


    def post(self):
        """
        Invoke do_plan method in assessment class to initiate assessment process
        """
        return planner.do_assessment(auth_url,dict(request.headers),auth_headers,api.payload)


@api.route('/containerization-planning', strict_slashes=False)
@api.doc(params={'catalog': {'description': 'catalog of container images: dockerhub, openshift or operator', 'in': 'query', 'type': 'string', 'default':'dockerhub', 'enum': ['dockerhub', 'openshift', 'operator']}})
class ContainerizationPlanning(Resource):
    """
    ContainerizationAssessment class creates the assessment in the form of assessment_model for the
    application/component details given in the input_model
    """
    @api.doc('create_containerization_planning')
    @api.response(201, 'Container recommendation generated!')
    @api.response(400, 'Input data format doesn\'t match the format expected by TCA')
    @api.response(401, 'Unauthorized, missing or invalid access token')
    @api.response(500, 'Internal Server Error, missing or wrong config of RBAC access token validation url')
    @api.expect([assessment_model])
    @api.marshal_with(output_model_planning)
    @api.doc(security='apikey')


    def post(self):
        """
        Invoke do_plan method in planning class to initiate planning process
        """

        catalog = request.args.get('catalog')

        if not catalog:
            catalog = 'dockerhub'
        catalog = catalog.lower()
        if catalog not in ['dockerhub', 'openshift', 'operator']:
            catalog = 'dockerhub'

        return planner.do_plan(auth_url,dict(request.headers),auth_headers,api.payload,catalog)

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
