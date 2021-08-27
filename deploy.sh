TCA_GITHUB_REPO=https://github.com/mihirc-github/tackle-container-advisor
TCA_GITHUB_BRANCH=os_kg_utils
TCA_GITHUB_DIR=aca_backend_api
TCA_DEPLOY_NAME=tca
OCP4_ACCESS_TOKEN=sha256~xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OCP4_API_SERVER=https://api.sandbox-m2.ll9k.p1.openshiftapps.com:6443


oc login --token=${OCP4_ACCESS_TOKEN} --server=${OCP4_API_SERVER}
oc projects
oc delete all --selector  app=tca
echo "Creating application from ${TCA_GITHUB_REPO}/${TCA_GITHUB_DIR}#${TCA_GITHUB_BRANCH}"
oc new-app ${TCA_GITHUB_REPO}#${TCA_GITHUB_BRANCH} --context-dir=${TCA_GITHUB_DIR} --name ${TCA_DEPLOY_NAME}
oc expose service ${TCA_DEPLOY_NAME}
oc get route ${TCA_DEPLOY_NAME}
