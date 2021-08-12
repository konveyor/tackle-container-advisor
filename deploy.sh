ACA_GITHUB_REPO=https://github.com/${GH_USER}/tackle-container-advisor
ACA_GITHUB_BRANCH=os_kg_utils
ACA_GITHUB_DIR=aca_backend_api
ACA_DEPLOY_NAME=aca
OCP4_ACCESS_TOKEN=sha256~yKP_8aQTwpGl1gZGNYfbK5hspd7bCFn5JMpKmszzOGs
OCP4_API_SERVER=https://api.sandbox-m2.ll9k.p1.openshiftapps.com:6443


oc login --token=${OCP4_ACCESS_TOKEN} --server=${OCP4_API_SERVER}
oc projects
oc delete all --selector  app=aca
echo "Creating application from ${ACA_GITHUB_REPO}/${ACA_GITHUB_DIR}#${ACA_GITHUB_BRANCH}"
oc new-app ${ACA_GITHUB_REPO}#${ACA_GITHUB_BRANCH} --context-dir=${ACA_GITHUB_DIR} --name ${ACA_DEPLOY_NAME}
oc expose service ${ACA_DEPLOY_NAME}
oc get route ${ACA_DEPLOY_NAME}
