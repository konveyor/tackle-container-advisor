# MIT License
#
# Copyright (c) 2017 Daniel Sullivan (mumblepins)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from __future__ import print_function

import json

import requests
from furl import furl
from requests.auth import AuthBase


class TimeoutError(Exception):
    pass


class ConnectionError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class DockerHubAuth(AuthBase):
    def __init__(self, requests_post, api_url, username=None, password=None, token=None, delete_creds=True):
        """

        Args:
            requests_post (:py:meth:`DockerHub._do_requests_post`):
            api_url (str):
            username (str, optional):
            password (str, optional):
            token (str, optional):
            delete_creds (bool, optional):
        """

        self._api_url = api_url
        self._requests_post = requests_post
        if token is not None:
            self._token = token
            return
        if username is not None and password is not None:
            self._username = username
            self._password = password
            self._get_authorization_token()
            if delete_creds:
                self._username = None
                self._password = None
            return
        raise ValueError("Need either username and password or token for authentication")

    @property
    def token(self):
        return self._token

    def __eq__(self, other):
        return self._token == getattr(other, '_token', None)

    def __ne__(self, other):
        return not self == other

    def __call__(self, r):
        r.headers['Authorization'] = "JWT {}".format(self._token)
        return r

    def _get_authorization_token(self):
        """Actually gets the authentication token

        Raises:
            AuthenticationError: didn't login right

        """
        r = self._requests_post(
                self._api_url,
                {
                    "username": self._username,
                    "password": self._password
                })
        if not r.ok:
            raise AuthenticationError("Error Status {}:\n{}".format(r.status_code, json.dumps(r.json(), indent=2)))
        self._token = r.json()['token']


def parse_url(url):
    """Parses a url into the base url and the query params

    Args:
        url (str): url with query string, or not

    Returns:
        (str, `dict` of `lists`): url, query (dict of values)
    """
    f = furl(url)
    query = f.args
    query = {a[0]: a[1] for a in query.listitems()}
    f.remove(query=True).path.normalize()
    url = f.url

    return url, query


def user_cleaner(user):
    """Converts none or _ to library, makes username lowercase

    Args:
        user (str):

    Returns:
        str: cleaned username

    """
    if user == "_" or user == "":
        return "library"
    try:
        return user.lower()
    except AttributeError:
        return user


class DockerHub(object):
    """Actual class for making API calls

    Args:
        username (str, optional):
        password(str, optional):
        token(str, optional):
        url(str, optional): Url of api (https://hub.docker.com)
        version(str, optional): Api version (v2)
        delete_creds (bool, optional): Whether to delete password after logging in (default True)
        return_lists (bool, optional): Whether to return a `generator` from calls that return multiple values
            (False, default), or to return a simple `list` (True)
    """

    # <editor-fold desc="Class Management">
    def __init__(self, username=None, password=None, token=None, url=None, version='v2', delete_creds=True,
                 return_lists=False):

        #https://registry.hub.docker.com/  
        # 'https://hub.docker.com'       

        self._version = version
        self._url = '{0}/{1}'.format(url or'https://registry.hub.docker.com' , self.version)
        self._session = requests.Session()
        self._auth = None
        self._token = None
        self._username = None
        self._password = None
        self._return_lists = return_lists
        self.login(username, password, token, delete_creds)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._session.close()

    # </editor-fold>

    # <editor-fold desc="Properties">
    @property
    def return_lists(self):
        """Whether functions should return generators (False) or lists (True)

        Returns:
            bool

        """
        return self._return_lists

    @return_lists.setter
    def return_lists(self, value):
        self._return_lists = value

    @property
    def username(self):
        if self._username is None and self.logged_in:
            self._get_username()
        return self._username

    @property
    def logged_in(self):
        return self.token is not None

    @property
    def version(self):
        return self._version

    @property
    def url(self):
        return self._url

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value
        self._get_username()

    # </editor-fold>

    # <editor-fold desc="Protected Methods">

    def _do_request(self, method, address, **kwargs):
        try:
            if 'timeout' not in kwargs:
                kwargs['timeout'] = (5, 15)

            if 'auth' not in kwargs:
                kwargs['auth'] = self._auth

            if 'headers' not in kwargs:
                kwargs['headers'] = {"Content-Type": "application/json"}
            elif 'Content-Type' not in kwargs['headers']:
                kwargs['headers']['Content-Type'] = "application/json"

            url, query = parse_url(address)
            if query:
                address = url
                if 'params' in kwargs:
                    query.update(kwargs['params'])
                kwargs['params'] = query
            resp = self._session.request(method, address, **kwargs)

        except requests.exceptions.Timeout as e:
            raise TimeoutError('Connection Timeout. Download failed: {0}'.format(e))
        except requests.exceptions.RequestException as e:
            raise ConnectionError('Connection Error. Download failed: {0}'.format(e))
        else:
            try:
                resp.raise_for_status()
            except:
                print(resp.json())
                print(resp.headers)
                raise
            return resp

    def _do_requests_get(self, address, **kwargs):
        if 'params' not in kwargs:
            kwargs['params'] = {}
        # if 'perPage' not in kwargs['params']:
        #     #kwargs['params']['perPage'] = 100
        #     pass
        return self._do_request('GET', address, **kwargs)

    def _do_requests_post(self, address, json_data=None, **kwargs):
        return self._do_request('POST', address, json=json_data, **kwargs)

    def _do_requests_put(self, address, json_data=None, **kwargs):
        return self._do_request('PUT', address, json=json_data, **kwargs)

    def _do_requests_patch(self, address, json_data, **kwargs):
        return self._do_request('PATCH', address, json=json_data, **kwargs)

    def _do_requests_delete(self, address, **kwargs):
        return self._do_request('DELETE', address, **kwargs)

    def _iter_requests_get(self, address, **kwargs):
        if self.return_lists:
            return list(self._iter_requests_get_generator(address, **kwargs))
        return self._iter_requests_get_generator(address, **kwargs)

    def _iter_requests_get_generator(self, address, **kwargs):
        _next = None
        resp = self._do_requests_get(address, **kwargs)

        while True:
            if _next:
                resp = self._do_requests_get(_next)
                # print _next

            resp = resp.json()

            for i in resp['results']:
                yield i

            if resp['next']:
                _next = resp['next']
                continue
            return

    def _api_url(self, path):
        return '{0}/{1}/'.format(self.url, path)

    def _get_username(self):
        if self.logged_in:
            self._username = user_cleaner(self.logged_in_user()['username'])
        else:
            self._username = None

    # </editor-fold>

    def login(self, username=None, password=None, token=None, delete_creds=True):
        """Logs into Docker hub and gets a token

        Either username and password or token should be specified

        Args:
            username (str, optional):
            password (str, optional):
            token (str, optional):
            delete_creds (bool, optional):

        Returns:

        """

        self._username = user_cleaner(username)
        self._password = password
        self._token = token
        if token is not None:
            # login with token
            self._auth = DockerHubAuth(self._do_requests_post, self._api_url('users/login'), token=token)
        elif username is not None and password is not None:
            # login with user/pass
            self._auth = DockerHubAuth(self._do_requests_post, self._api_url('users/login'), username=username,
                                       password=password)
        else:
            # don't login
            return

        if delete_creds:
            self._password = None

        self._token = self._auth.token

    def comments(self, user, repository, **kwargs):
        """

        Args:
            user:
            repository:
            **kwargs:

        Returns:

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{0}/{1}/comments'.format(user, repository))
        return self._iter_requests_get(url, **kwargs)

    def repository(self, user, repository, **kwargs):
        """

        Args:
            user:
            repository:
            **kwargs:

        Returns:

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{0}/{1}'.format(user, repository))
        return self._do_requests_get(url, **kwargs).json()

    def repositories(self, user, **kwargs):
        """

        Args:
            user:
            **kwargs:

        Returns:

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{0}'.format(user))
        return self._iter_requests_get(url, **kwargs)

    def repositories_starred(self, user, **kwargs):
        """

        Args:
            user:
            **kwargs:

        Returns:

        """
        user = user_cleaner(user)
        url = self._api_url('users/{0}/repositories/starred'.format(user))
        return self._iter_requests_get(url, **kwargs)

    def tags(self, user, repository, **kwargs):
        """

        Args:
            user:
            repository:
            **kwargs:

        Returns:

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{0}/{1}/tags'.format(user, repository))
        return self._iter_requests_get(url, **kwargs)

    def user(self, user, **kwargs):
        """

        Args:
            user:
            **kwargs:

        Returns:

        """
        user = user_cleaner(user)
        url = self._api_url('users/{0}'.format(user))
        return self._do_requests_get(url, **kwargs).json()

    # ------ Logged In Section

    def logged_in_user(self):
        """

        Returns:

        """
        return self._do_requests_get(self._api_url('user')).json()

    def add_collaborator(self, user, repository, collaborator):
        """

        Args:
            user:
            repository:
            collaborator:

        Returns:

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}/collaborators'.format(user, repository))
        return self._do_requests_post(url, {
            "user": collaborator.lower()
        }).json()

    def build_details(self, user, repository, code):
        """

        Args:
            user:
            repository:
            code:

        Returns:

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}/buildhistory/{}'.format(user, repository, code))
        return self._do_requests_get(url).json()

    def build_history(self, user, repository, **kwargs):
        """

        Args:
            user:
            repository:
            **kwargs:

        Returns:

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}/buildhistory'.format(user, repository))
        return self._iter_requests_get(url, **kwargs)

    def build_links(self, user, repository, **kwargs):
        """

        Args:
            user:
            repository:
            **kwargs:

        Returns:

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}/links'.format(user, repository))
        return self._iter_requests_get(url, **kwargs)

    def build_settings(self, user, repository):
        """

        Args:
            user:
            repository:

        Returns:

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}/autobuild'.format(user, repository))
        return self._do_requests_get(url).json()

    def build_trigger(self, user, repository):
        """

        Args:
            user:
            repository:

        Returns:

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}/buildtrigger'.format(user, repository))
        return self._do_requests_get(url).json()

    def build_trigger_history(self, user, repository, **kwargs):
        """

        Args:
            user:
            repository:
            **kwargs:

        Returns:

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}/buildtrigger/history'.format(user, repository))
        return self._iter_requests_get(url, **kwargs)

    def collaborators(self, user, repository, **kwargs):
        """

        Args:
            user:
            repository:
            **kwargs:

        Returns:

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}/collaborators'.format(user, repository))
        return self._iter_requests_get(url, **kwargs)

    def create_build_link(self, user, repository, to_repo):
        """

        Args:
            user:
            repository:
            to_repo:

        Returns:

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}/links'.format(user, repository))
        return self._do_requests_post(url, {
            "to_repo": to_repo
        }).json()

    def create_build_tag(self, user, repository, details):
        """

        Args:
            user:
            repository:
            details:

        Returns:

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}/autobuild/tags'.format(user, repository))
        return self._do_requests_post(url, {
            'isNew':               True,
            'namespace':           user,
            'repoName':            repository,
            'name':                details['name'] if 'name' in details else 'latest',
            'dockerfile_location': details['dockerfile_location'] if 'dockerfile_location' in details else '/',
            'source_type':         details['source_type'] if 'source_type' in details else 'Branch',
            'source_name':         details['source_name'] if 'source_name' in details else 'master'
        }).json()

    def create_repository(self, user, repository, details):
        """

        Args:
            user:
            repository:
            details:

        Returns:

        """
        user = user_cleaner(user)
        url = self._api_url('repositories')
        data = {
            'name':      repository,
            'namespace': user,
        }
        details.update(data)
        return self._do_requests_post(url, details).json()

    def create_automated_build(self, user, repository, details):
        """

        Args:
            user:
            repository:
            details:

        Returns:

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}/autobuild'.format(user, repository))
        data = {
            'name':                repository,
            'namespace':           user,
            'active':              True,
            'dockerhub_repo_name': "{}/{}".format(user, repository)
        }

        details.update(data)
        return self._do_requests_post(url, details).json()

    def create_webhook(self, user, repository, webhook_name):
        """

        Args:
            user:
            repository:
            webhook_name:

        Returns:

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}/webhooks'.format(user, repository))
        data = {
            'name': webhook_name
        }
        return self._do_requests_post(url, data).json()

    def create_webhook_hook(self, user, repository, webhook_id, webhook_url):
        """

        Args:
            user:
            repository:
            webhook_id:
            webhook_url:

        Returns:

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}/webhooks/{}/hooks'.format(user, repository, webhook_id))
        data = {
            'hook_url': webhook_url
        }
        return self._do_requests_post(url, data).json()

    def delete_build_link(self, user, repository, build_id):
        """

        Args:
            user:
            repository:
            build_id:

        Returns:
            boolean: returns true if successful delete call

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}/links/{}'.format(user, repository, build_id))
        resp = self._do_requests_delete(url)
        # print_response(resp)
        return resp.status_code == 204

    def delete_build_tag(self, user, repository, tag_id):
        """

        Args:
            user:
            repository:
            tag_id:

        Returns:
            boolean: returns true if successful delete call

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}/autobuild/tags/{}'.format(user, repository, tag_id))
        resp = self._do_requests_delete(url)
        return resp.status_code == 204

    def delete_tag(self, user, repository, tag):
        """

        Args:
            user:
            repository:
            tag:

        Returns:
            boolean: returns true if successful delete call

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}/tags/{}'.format(user, repository, tag))
        resp = self._do_requests_delete(url)
        return resp.status_code == 204

    def delete_collaborator(self, user, repository, collaborator):
        """

        Args:
            user:
            repository:
            collaborator:

        Returns:
            boolean: returns true if successful delete call

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}/collaborators/{}'.format(user, repository, collaborator.lower()))
        resp = self._do_requests_delete(url)
        return resp.status_code in [200, 201, 202, 203, 204]

    def delete_repository(self, user, repository):
        """

        Args:
            user:
            repository:

        Returns:
            boolean: returns true if successful delete call

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}'.format(user, repository))
        resp = self._do_requests_delete(url)
        # print_response(resp)
        return resp.status_code in [200, 201, 202, 203, 204]

    def delete_webhook(self, user, repository, webhook_id):
        """

        Args:
            user:
            repository:
            webhook_id:

        Returns:
            boolean: returns true if successful delete call

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}/webhooks/{}'.format(user, repository, webhook_id))
        resp = self._do_requests_delete(url)
        # print_response(resp)
        return resp.status_code in [200, 201, 202, 203, 204]

    def registry_settings(self):
        """

        Returns:

        """
        url = self._api_url('users/{}/registry-settings'.format(self.username))
        return self._do_requests_get(url).json()

    def set_build_tag(self, user, repository, build_id, details):
        """

        Args:
            user:
            repository:
            build_id:
            details:

        Returns:

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}/autobuild/tags/{}'.format(user, repository, build_id))
        data = {
            'id':                  build_id,
            'name':                'latest',
            'dockerfile_location': '/',
            'source_type':         'Branch',
            'source_name':         'master'
        }
        data.update(details)
        return self._do_requests_put(url, details).json()

    def set_repository_description(self, user, repository, descriptions):
        """

        Args:
            user:
            repository:
            descriptions:

        Returns:

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}'.format(user, repository))
        data = {}
        if 'full' in descriptions:
            data['full_description'] = descriptions['full']
        if 'short' in descriptions:
            data['description'] = descriptions['short']
        if not data:
            raise ValueError("Need either 'short' or 'full' description specified")

        return self._do_requests_patch(url, data).json()

    def star_repository(self, user, repository):
        """

        Args:
            user:
            repository:

        Returns:
            boolean: returns true if successful

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}/stars'.format(user, repository))
        resp = self._do_requests_post(url, {})
        # print_response(resp)
        return resp.status_code in [200, 201, 202, 203, 204]

    def unstar_repository(self, user, repository):
        """

        Args:
            user:
            repository:

        Returns:
            boolean: returns true if successful

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}/stars'.format(user, repository))
        resp = self._do_requests_delete(url)
        # print_response(resp)
        return resp.status_code in [200, 201, 202, 203, 204]

    def trigger_build(self, user, repository, details):
        """

        Args:
            user:
            repository:
            details:

        Returns:

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}/autobuild/trigger-build'.format(user, repository))
        data = {
            'dockerfile_location': '/',
            'source_type':         'Branch',
            'source_name':         'master'
        }
        data.update(details)
        return self._do_requests_post(url, data).json()

    def webhooks(self, user, repository, **kwargs):
        """

        Args:
            user:
            repository:
            **kwargs:

        Returns:

        """
        user = user_cleaner(user)
        url = self._api_url('repositories/{}/{}/webhooks'.format(user, repository))
        return self._iter_requests_get(url, **kwargs)