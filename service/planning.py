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

import os
import json
from collections import OrderedDict
import logging
import codecs
from service.utils import Utils
import re

import configparser

config = configparser.ConfigParser()
common = os.path.join("config", "common.ini")
kg     = os.path.join("config", "kg.ini")
config.read([common, kg])


class Plan():
    def __init__(self, logger=False):
        '''
        Loads the docker, openshift and operator KG json file data
        '''

        logging.basicConfig(level=logging.INFO)

        dockerimageKG_filepath = os.path.join(config['general']['kg_dir'], config['filenames']['dockerimageKG'])
        if os.path.exists(dockerimageKG_filepath):   
            with open(dockerimageKG_filepath, 'r') as f:
                self.__dockerimage_KG = json.load(f)
        else:
            self.__dockerimage_KG = {}
            logging.error(f'dockerimageKG[{dockerimageKG_filepath}] is empty or not exists')

        baseOSKG_filepath = os.path.join(config['general']['kg_dir'], config['filenames']['baseOSKG'])
        self.__osBaseImages = {}
        if os.path.exists(baseOSKG_filepath):
            with open(baseOSKG_filepath, 'r') as f:
                baseOSKG = json.load(f)

            for image_name in baseOSKG['Container Images']:
                self.__osBaseImages[baseOSKG['Container Images'][image_name]['OS'][0]['Class']] = image_name
                self.__dockerimage_KG['Container Images'][image_name] = baseOSKG['Container Images'][image_name]
        else:
            logging.error(f'baseOSKG[{baseOSKG_filepath}] is empty or not exists')

        inverted_dockerimageKG_filepath = os.path.join(config['general']['kg_dir'], config['filenames']['inverted_dockerimageKG'])
        if os.path.exists(inverted_dockerimageKG_filepath):
            with open(inverted_dockerimageKG_filepath, 'r') as f:
                self.__inverted_dockerimageKG = json.load(f)
        else:
            self.__inverted_dockerimageKG = {}
            logging.error(f'inverted_dockerimageKG[{inverted_dockerimageKG_filepath}] is empty or not exists')

        ##Openshift images
        openshiftimageKG_filepath = os.path.join(config['general']['kg_dir'], config['filenames']['openshiftimageKG'])
        if os.path.exists(openshiftimageKG_filepath):
            with open(openshiftimageKG_filepath, 'r') as f:
                self.__openshiftimage_KG = json.load(f)
        else:
            self.__openshiftimage_KG = {}
            logging.error(f'openshiftimageKG[{openshiftimageKG_filepath}] is empty or not exists')

        openshiftbaseOSKG_filepath = os.path.join(config['general']['kg_dir'], config['filenames']['openshiftbaseOSKG'])
        self.__openshiftosBaseImages = {}
        if os.path.exists(openshiftbaseOSKG_filepath):
            with open(openshiftbaseOSKG_filepath, 'r') as f:
                openshiftbaseOSKG = json.load(f)

            for image_name in openshiftbaseOSKG['Container Images']:
                self.__openshiftosBaseImages[openshiftbaseOSKG['Container Images'][image_name]['OS'][0]['Class']] = image_name
                self.__openshiftimage_KG['Container Images'][image_name] = openshiftbaseOSKG['Container Images'][image_name]
        else:
            logging.error(f'openshiftbaseOSKG[{openshiftbaseOSKG_filepath}] is empty or not exists')

        inverted_openshiftimageKG_filepath = os.path.join(config['general']['kg_dir'], config['filenames']['inverted_openshiftimageKG'])
        if os.path.exists(inverted_openshiftimageKG_filepath):
            with open(inverted_openshiftimageKG_filepath, 'r') as f:
                self.__inverted_openshiftimageKG = json.load(f)
        else:
            self.__inverted_openshiftimageKG = {}
            logging.error(f'inverted_openshiftimageKG[{inverted_openshiftimageKG_filepath}] is empty or not exists')

        ##Operator images
        operatorimageKG_filepath = os.path.join(config['general']['kg_dir'], config['filenames']['operatorimageKG'])
        if os.path.exists(operatorimageKG_filepath):
            with open(operatorimageKG_filepath, 'r') as f:
                self.__operatorimage_KG = json.load(f)
        else:
            self.__operatorimage_KG = {}
            logging.error(f'operatorimageKG[{operatorimageKG_filepath}] is empty or not exists')

        if os.path.exists(baseOSKG_filepath):
            with open(baseOSKG_filepath, 'r') as f:
                baseOSKG = json.load(f)

            for image_name in baseOSKG['Container Images']:
                self.__operatorimage_KG['Container Images'][image_name] = baseOSKG['Container Images'][image_name]
        else:
            logging.error(f'baseOSKG[{baseOSKG_filepath}] is empty or not exists')

        inverted_operatorimageKG_filepath = os.path.join(config['general']['kg_dir'], config['filenames']['inverted_operatorimageKG'])
        if os.path.exists(inverted_operatorimageKG_filepath):
            with open(inverted_operatorimageKG_filepath, 'r') as f:
                self.__inverted_operatorimageKG = json.load(f)
        else:
            self.__inverted_operatorimageKG = {}
            logging.error(f'inverted_operatorimageKG[{inverted_operatorimageKG_filepath}] is empty or not exists')


        COTSKG_filepath = os.path.join(config['general']['kg_dir'], config['filenames']['COTSKG'])
        if os.path.exists(COTSKG_filepath):
            with open(COTSKG_filepath, 'r') as f:
                self.__COTSKG = json.load(f)
        else:
            self.__COTSKG = {}
            logging.error(f'COTSKG[{COTSKG_filepath}] is empty or not exists')


        if logger == True:
            self.logfile = codecs.open('logfile.txt','w',encoding='utf-8')

        self.MAJOR_VERSION_NUMBER_REGEX = re.compile('([0-9]+)')

    def __compute_confidence(self, app, catalog = 'dockerhub'):
        """
        Selects the best image for each detected entities and compute the overall confidence for the component.

        :param app: list of application/component details
                catalog: A string containing catalog name to fetch the corresponding images

        :returns: Updated application/component details with selected best images and confidence score

        """
        scores_dict = {'OS': 40, 'App': 20, 'App Server': 20, 'Runtime': 10, 'Lang': 10,'unknown':10}

        scope_images = app['scope_images']
        app['scope_images'] = {}
        app['scope_images_confidence'] = {}
        app['scope_images_confidence']['mapping'] = {}
        child_types = ["App Server", "App", "Runtime","Lang"]

        inverted_containerimageKG = self.__inverted_dockerimageKG
        containerimageKG = self.__dockerimage_KG
        imageurl = 'Docker_URL'
        if catalog == 'openshift':
            inverted_containerimageKG = self.__inverted_openshiftimageKG
            containerimageKG = self.__openshiftimage_KG
        if catalog == 'operator':
            inverted_containerimageKG = self.__inverted_operatorimageKG
            containerimageKG = self.__operatorimage_KG

        # Compute maximum value of confidence
        cum_scores = scores_dict['OS']

        cum_scores += len(app['unknown']) * scores_dict['unknown']

        for child_type in child_types:
            if app[child_type] != '':
                cum_scores += len(app[child_type].split(', '))*scores_dict[child_type]

        if not scope_images:
            app['scope_images_confidence']['images_score'] = 0
            app['scope_images_confidence']['cum_scores'] = cum_scores
            app['scope_images_confidence']['image_confidence'] = 0
            app['scope_images_confidence']['custom_installations_needed'] = []
            app['scope_images_confidence']['custom_images_needed'] = []
            app['scope_images_confidence']['mapping'] = {}
            return app

        covered_lang = []
        images_score = scores_dict['OS']
        custom_installations_needed = []
        custom_images_needed = []
        lang_needed = app['Lang'].split(', ')
        child_types = ['App Server', 'App', 'Runtime']
        app_appserver_child_types = ['App Server', 'App']
        has_images_for_app_appserver = False
        for child_type in child_types:
            for child in app[child_type].split(', '):
                if child:
                    if child in inverted_containerimageKG:
                        candidated_images = []
                        for scope_image in scope_images:
                            if scope_image in inverted_containerimageKG[child]:
                                candidated_images.append(scope_image)
                        if len(candidated_images) > 0:
                            #select best images using image status
                            best_image = candidated_images[0]
                            for scope_image in candidated_images:
                                status = containerimageKG['Container Images'][scope_image].get('CertOfImageAndPublisher')
                                if status and len(status) > 0:
                                    best_image = scope_image
                                    break
                            scope_image = best_image
                            images_score += scores_dict[child_type]
                            # print(str(scope_image))
                            app['scope_images'][scope_image] = {'Docker_URL': containerimageKG['Container Images'][scope_image][imageurl], 'Status': containerimageKG['Container Images'][scope_image].get('CertOfImageAndPublisher')}
                            app['scope_images_confidence']['mapping'][child] = scope_image
                            if child_type in app_appserver_child_types:
                                has_images_for_app_appserver = True
                            lang = containerimageKG['Container Images'][scope_image]['Lang']
                            if lang and len(lang) > 0 and lang_needed and len(lang_needed) > 0:
                                for langObj in lang:
                                    if langObj['Class'] in lang_needed:
                                        covered_lang.append(langObj['Class'])
                                        images_score += scores_dict['Lang']
                        else:
                            if child_type in app_appserver_child_types:
                                custom_images_needed.append(child)
                            else:
                                custom_installations_needed.append(child)
                    else:
                        if child_type in app_appserver_child_types:
                            custom_images_needed.append(child)
                        else:
                            custom_installations_needed.append(child)

        if 'Windows' in app['OS'] and has_images_for_app_appserver:
            # remove Runtime to custom_installations_needed if needed
            child_type = 'Runtime'
            if app[child_type]:
                for child in app[child_type].split(', '):
                    if child and child in inverted_containerimageKG:
                        for scope_image in app['scope_images']:
                            if scope_image in inverted_containerimageKG[child]:
                                # delete this scop_image
                                del app['scope_images'][scope_image]
                                for k,v in app['scope_images_confidence']['mapping'].items():
                                    if v == scope_image:
                                        del app['scope_images_confidence']['mapping'][k]
                                        break
                                images_score -= scores_dict[child_type]
                                custom_installations_needed.append(child)
                                ## todo: remove covered lang if needed
                                break

        if len(app['scope_images']) > 0:
            has_images_for_app_appserver = True
        for child in lang_needed:
            if child:
                if child in covered_lang:
                    continue
                if child in inverted_containerimageKG:
                    candidated_images = []
                    for scope_image in scope_images:
                        if scope_image in inverted_containerimageKG[child] and len(containerimageKG['Container Images'][scope_image]['App']) == 0 and len(containerimageKG['Container Images'][scope_image]['App Server']) == 0 and len(containerimageKG['Container Images'][scope_image]['Runtime']) == 0:
                            # Pure lang docker
                            if not has_images_for_app_appserver:
                                candidated_images.append(scope_image)
                    if len(candidated_images) > 0:
                        #select best images using image status
                        best_image = candidated_images[0]
                        for scope_image in candidated_images:
                            status = containerimageKG['Container Images'][scope_image].get('CertOfImageAndPublisher')
                            if status and len(status) > 0:
                                best_image = scope_image
                                break
                        scope_image = best_image
                        images_score += scores_dict['Lang']
                        app['scope_images'][scope_image] = {'Docker_URL': containerimageKG['Container Images'][scope_image][imageurl], 'Status': containerimageKG['Container Images'][scope_image].get('CertOfImageAndPublisher')}
                        app['scope_images_confidence']['mapping'][child] = scope_image
                    else:
                        custom_installations_needed.append(child)
                else:
                    custom_installations_needed.append(child)

        if not app['scope_images'] and scope_images:
            # find best for OS
            scope_image = scope_images[0]
            # print(scope_image)
            app['scope_images'][scope_image] = {'Docker_URL': containerimageKG['Container Images'][scope_image][imageurl], 'Status': containerimageKG['Container Images'][scope_image].get('CertOfImageAndPublisher')}
            # app['scope_images_confidence']['mapping'][child] = scope_image


        app['scope_images_confidence']['image_confidence'] = round(images_score/cum_scores,3)
        app['scope_images_confidence']['images_score'] = images_score
        app['scope_images_confidence']['cum_scores'] = cum_scores
        app['scope_images_confidence']['custom_installations_needed'] = custom_installations_needed
        app['scope_images_confidence']['custom_images_needed'] = custom_images_needed

        ## ToDo
        ## Update confidence according to version match

        return app


    def __search_docker(self, app, catalog = 'dockerhub'):

        """
        Searches the docker or openshift images for each detected entities based on selected catalog.

        :param app: list of application/component details
                catalog: A string containing catalog name to fetch the corresponding images

        :returns: Updated application/component details with detected docker or openshift images

        """
        if (not app) or ('OS' not in app) or ('App Server' not in app) or ('App' not in app) or ('Runtime' not in app) or ('Lang' not in app):
            return app
        if app['OS'] == '':
            return app
        osBaseImages = self.__osBaseImages
        inverted_containerimageKG = self.__inverted_dockerimageKG
        if catalog == 'openshift':
            osBaseImages = self.__openshiftosBaseImages
            inverted_containerimageKG = self.__inverted_openshiftimageKG
        if catalog == 'operator':
            inverted_containerimageKG = self.__inverted_operatorimageKG

        app['scope_images'] = []
        backup_images = []
        if app['OS'] in osBaseImages:
            backup_images.append(osBaseImages[app['OS']])
        else:
            for os in osBaseImages:
                if os == app['OS'] or os == app['OS'].split('|')[0] or os.split('|')[0] == app['OS'].split('|')[0]:
                    backup_images.append(osBaseImages[os])
                    break
        full_os_check_images = []
        parent_os_check_iamges = []
        if app['OS'] in inverted_containerimageKG:
            full_os_check_images = inverted_containerimageKG[app['OS']]
        if (app['OS'].split('|')[0] != app['OS']) and app['OS'].split('|')[0] in inverted_containerimageKG:
            parent_os_check_iamges = inverted_containerimageKG[app['OS'].split('|')[0]]

        # parent_os_scope_images = []
        child_types = ["App Server", "App", "Runtime","Lang"]
        for child_type in child_types:
            for child in app[child_type].split(', '):
                # Use inverted index to find dockerimage and check its OS
                if child and child in inverted_containerimageKG:
                    for image_name in inverted_containerimageKG[child]:
                        if ((image_name in full_os_check_images) or (image_name in parent_os_check_iamges)) and (image_name not in app['scope_images']):
                            app['scope_images'].append(image_name)

        # add base image for the OS if no element in tech stack has a pre-existing image
        if not app['scope_images']:
            if set(backup_images):
                app['scope_images'] = list(set(backup_images))
        return app


    def __find_best_os(self, app, os):

        """
        Find the best operating system
        :param app: list of application/component details
                    os: A string contains operating system value

        :returns: best operating system value

        """
        linux_list = ['Linux|Red Hat Enterprise Linux', 'Linux|Ubuntu', 'Linux|CentOS', 'Linux|Fedora', 'Linux|Debian', '	Linux|Oracle Linux', '	Linux|openSUSE', '	Linux|Amazon Linux']
        result = os
        for inputOS in Utils.getEntityString(app['OS']).split(', '):
            if inputOS and '|' in inputOS and os == inputOS.split('|')[0]:
                result = inputOS
                break
        if os == 'Linux':
            for linuxOS in linux_list:
                if linuxOS in app['OS']:
                    result = linuxOS
                    break
        return result

    def ui_to_input_assessment(self, assessment_data):
        """
        ui_to_input_assessment method takes the assessment ouput and format it to list of application details
        which will be further used for planning

        :param assessment_data: list of assessment output for each component

        :returns: list of formatted application details to be processed in planning

        """
        pAppL = []

        try:
            for app in assessment_data:
                # Order dictionry to fix the order of columns in the output
                pApp = OrderedDict()

                # Raw Fields
                pApp['application_name'] = ''
                if 'Name' in app:
                    pApp['application_name'] = app["Name"]

                pApp['application_description'] = ''
                if 'Desc' in app:
                    pApp['application_description'] = app["Desc"]

                pApp['component_name'] = ''
                if 'Cmpt' in app:
                    pApp['component_name'] = app["Cmpt"]

                # Curated
                pApp['OS'] = eval(app["OS"])
                pApp['Lang'] = eval(app["Lang"])
                pApp["App Server"] = eval(app["App Server"])
                pApp["App"] = eval(app["Dependent Apps"])
                pApp["Runtime"] = eval(app["Runtime"])
                pApp["Lib"] = eval(app["Libs"])

                pApp['assessment_reason'] = app['Reason']
                try:
                    pApp["KG Version"] = app["KG Version"]
                except:
                    pApp["KG Version"] = 'Not Available'


                pAppL.append(pApp)

            return pAppL

        except Exception as e:
            logging.error(str(e))


    def validate_app(self,appL):
        """
        validate_app methods validates each component if it's having any OS or RepackageOS value and set valid_assessment
        value accordingly.

        :param appL: list of application details

        :returns: list of application details with updated valid_assessment values
        """
        try:
            for app in appL:
                app['valid_assessment'] = True
                if not app['OS'] and len(app['RepackageOS']) == 0:
                    app['valid_assessment'] = False

            return appL

        except Exception as e:
            logging.error(str(e))

    ############ Map to Docker
    def map_to_docker(self, appL, catalog = 'dockerhub'):
        """
        validate_app methods validates each component if it's having any OS or RepackageOS value and set valid_assessment
        value accordingly.

        :param appL: list of application details

        :returns: list of application details with updated valid_assessment values

        """
        if len(self.__dockerimage_KG) == 0 or len(self.__osBaseImages) == 0 or len(self.__inverted_dockerimageKG) == 0:
            logging.error('service/containerize_planning.py init failed')
            return appL
        if len(self.__openshiftimage_KG) == 0 or len(self.__openshiftosBaseImages) == 0 or len(self.__inverted_openshiftimageKG) == 0:
            logging.error('service/containerize_planning.py init failed')
            return appL
        if len(self.__operatorimage_KG) == 0 or len(self.__inverted_operatorimageKG) == 0:
            logging.error('service/containerize_planning.py init failed')
            return appL

        containerL = []
        for app in appL:
            if app['valid_assessment']:
                app['valid_planning'] = True
                app['planning_reason'] = ""
                app['scope_images'] = []
                app['scope_images_confidence'] = {}



                if len(app['RepackageOS']) > 0:
                    ## Means input need several OS to containerize
                    targetOS = ['Linux', 'Windows']
                    for os in targetOS:
                        if os in app['RepackageOS']:
                            subapp = {}
                            subapp['valid_assessment'] = True
                            subapp['valid_planning'] = True
                            subapp['planning_reason'] = ""
                            subapp['scope_images'] = []
                            subapp['scope_images_confidence'] = {}
                            subapp['OS'] = self.__find_best_os(app, os)
                            for child_type in app[os]:
                                subapp[child_type] = ', '.join(filter(None, app[os][child_type]))
                            subapp = self.__search_docker(subapp, catalog)
                            try:
                                subapp['unknown'] = app['unknown']
                            except Exception :
                                subapp['unknown'] = []
                            subapp = self.__compute_confidence(subapp, catalog)
                            if os == 'Windows' and len(app['RepackageOS']) == 2:
                                app['scope_images_win'] = subapp['scope_images']
                                app['scope_images_confidence_win'] = subapp['scope_images_confidence']
                            else:
                                app['scope_images'] = subapp['scope_images']
                                app['scope_images_confidence'] = subapp['scope_images_confidence']
                    if not app['scope_images']:
                        # No matching image found for the OS
                        app['valid_planning'] = False
                        app['planning_reason'] = "Reason 400: OS not supported by any container image: "+Utils.getEntityString(app['OS'])
                else:
                    ## recomend the base OS
                    child_types = ['App Server', 'App', 'Runtime', 'Lang']
                    targetOS = ['Linux', 'Windows']
                    for os in targetOS:
                        if os in Utils.getEntityString(app['OS']):
                            subapp = {}
                            subapp['valid_assessment'] = True
                            subapp['valid_planning'] = True
                            subapp['planning_reason'] = ""
                            subapp['scope_images'] = []
                            subapp['scope_images_confidence'] = {}
                            subapp['OS'] = self.__find_best_os(app, os)
                            for child_type in child_types:
                                subapp[child_type] = ''
                            subapp = self.__search_docker(subapp, catalog)
                            try:
                                subapp['unknown'] = app['unknown']
                            except Exception :
                                subapp['unknown'] = []
                            subapp = self.__compute_confidence(subapp, catalog)
                            if os == 'Windows' and 'Linux' in app['OS']:
                                app['scope_images_win'] = subapp['scope_images']
                                app['scope_images_confidence_win'] = subapp['scope_images_confidence']
                            else:
                                app['scope_images'] = subapp['scope_images']
                                app['scope_images_confidence'] = subapp['scope_images_confidence']

                    if not app['scope_images']:
                        # No matching image found for the OS
                        app['valid_planning'] = False
                        app['planning_reason'] = "Reason 400: OS not supported by any container image: "+Utils.getEntityString(app['OS'])


                containerL.append(app)

        return containerL

    ############ Show planning results to the UI
    def output_to_ui_planning(self, containerL):

        pAppL = []
        for app in containerL:
            # Order dictionry to fix the order of columns in the output
            pApp = OrderedDict()

            # Raw Data
            pApp['Name'] = ''
            if 'application_name' in app:
                pApp['Name'] = app["application_name"]
            pApp['Desc'] = ''
            if 'application_description' in app:
                pApp['Desc'] = app["application_description"]
            pApp['Cmpt'] = ''
            if 'component_name' in app:
                pApp['Cmpt'] = app["component_name"]

            # AI Insights
            pApp['Valid'] = app["valid_planning"]

            pApp["Ref Dockers"] = ""
            pApp["Confidence"] = 0
            pApp['Reason'] = app["planning_reason"]

            if app['scope_images']:
                if 'Containerize_Not_Supported Tech' in app and app['Containerize_Not_Supported Tech']:
                    reason = f"{app['Containerize_Not_Supported Tech']} can not be supported in any container image. "
                else:
                    reason = ''
                counter = 1
                counter_list = ''

                for image in app["scope_images"]:
                    image_name = image
                    docker_url_dict = {}
                    if app['scope_images'][image]['Status']:
                        image_name = image_name + '(' + app['scope_images'][image]['Status'] + ')'
                    docker_url_dict[image_name] = app["scope_images"][image]["Docker_URL"]
                    pApp['Ref Dockers'] += str(counter) + ". " + str(docker_url_dict) +'\n'
                    counter_list += str(counter) + ','
                    counter += 1
                counter_list = counter_list[:-1]
                if app['scope_images_confidence'] and app['scope_images_confidence']['custom_installations_needed']:
                    pApp['Reason'] += 'Additional Installations in container image ' + counter_list + ': ' + ', '.join(filter(None, app['scope_images_confidence']['custom_installations_needed']))

                if app['scope_images_confidence']:
                    pApp["Confidence"] = app['scope_images_confidence']['image_confidence']
                if 'scope_images_win' in app and app['scope_images_win']:
                    counter_list = ''
                    for image in app["scope_images_win"]:
                        image_name = image
                        if app['scope_images_win'][image]['Status']:
                            image_name = image_name + '(' + app['scope_images_win'][image]['Status'] + ')'
                        pApp['Ref Dockers'] += str(counter) + ". " + image_name +'|'+app["scope_images_win"][image]["Docker_URL"]+'\n'
                        counter_list += str(counter) + ','
                        counter += 1
                    counter_list = counter_list[:-1]
                    if 'scope_images_confidence_win' in app and app['scope_images_confidence_win'] and app['scope_images_confidence_win']['custom_installations_needed']:
                        if pApp['Reason']:
                            pApp['Reason'] += '\n '
                        pApp['Reason'] += 'Additional Installations in container image ' + counter_list + ':' + ', '.join(filter(None, app['scope_images_confidence_win']['custom_installations_needed']))

                    if 'scope_images_confidence_win' in app and app['scope_images_confidence_win']:
                        pApp["Confidence"] = round((app['scope_images_confidence']['images_score'] + app['scope_images_confidence_win']['images_score'])/(app['scope_images_confidence']['cum_scores'] + app['scope_images_confidence_win']['cum_scores']),3)
                elif 'Windows' in app['RepackageOS']:
                    ## Openshift env, Windows does not contain any base OS
                    win_not_supported = []
                    for child_type in app['Windows']:
                        if app['Windows'][child_type]:
                            win_not_supported.extend(app['Windows'][child_type])
                    if win_not_supported:
                        if 'scope_images_confidence_win' in app and app['scope_images_confidence_win']:
                            pApp["Confidence"] = (app['scope_images_confidence']['images_score'] + app['scope_images_confidence_win']['images_score'])/(app['scope_images_confidence']['cum_scores'] + app['scope_images_confidence_win']['cum_scores'])

                        if pApp['Reason']:
                            pApp['Reason'] += '\n '
                        pApp['Reason'] += 'Reason 400: Not supported by any container image: ' + ', '.join(filter(None, win_not_supported))
                        app["valid_planning"] = False
                pApp['Ref Dockers'] = pApp['Ref Dockers'][:-1]
                pApp["Confidence"] = round(pApp['Confidence'], 2)
                if pApp["Confidence"] == 1:
                    if reason:
                        reason = reason + ' '
                    pApp['Reason'] = reason + 'No additonal installations required.'
                else:
                    pApp['Reason'] = reason + pApp['Reason']

                custom_images_needed = []
                if 'scope_images_confidence' in app and app['scope_images_confidence'] and 'custom_images_needed' in app['scope_images_confidence'] and app['scope_images_confidence']['custom_images_needed']:
                    custom_images_needed.extend(app['scope_images_confidence']['custom_images_needed'])
                if 'scope_images_confidence_win' in app and app['scope_images_confidence_win'] and 'custom_images_needed' in app['scope_images_confidence_win'] and app['scope_images_confidence_win']['custom_images_needed']:
                    custom_images_needed.extend(app['scope_images_confidence_win']['custom_images_needed'])

                if custom_images_needed:
                    if pApp['Reason']:
                        pApp['Reason'] = pApp['Reason'] + '\n '
                    cots = []
                    cots_app = []
                    if self.__COTSKG and 'COTS' in self.__COTSKG and self.__COTSKG['COTS']:
                        cots = self.__COTSKG['COTS']
                    for x in custom_images_needed:
                        if x in cots or (x + '|*') in cots:
                            cots_app.append(x)
                    if cots_app:
                        pApp['Reason'] += 'Containerization feasibility unknown for COTS applications: ' + ', '.join(filter(None, cots_app))
                    non_cots_app = list(set(custom_images_needed) - set(cots_app))
                    if non_cots_app:
                        if pApp['Reason']:
                            pApp['Reason'] = pApp['Reason'] + '\n '
                        pApp['Reason'] += 'Containerization feasibility unknown for non-COTS applications: ' + ', '.join(filter(None, non_cots_app))

            pApp['Recommend'] = "Containerize"
            if not app["valid_planning"]:
                pApp['Recommend'] = "Keep"
            if 'reHost' in app and app['reHost']:
                pApp['Recommend'] = 'ReHost'
            if ('Reason' in app['assessment_reason'] and 'Reason' not in pApp['Reason']) or \
                'Containerization feasibility unknown' in pApp['Reason'] or \
                'can not be supported in any container image' in pApp['Reason']:
                pApp['Recommend'] = 'Partially Containerize'



            pAppL.append(pApp)
        return pAppL

    # MAJOR_VERSION_NUMBER_REGEX = re.compile('([0-9]+)')
