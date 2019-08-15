import io
import atexit
from functools import wraps

import requests

from xnat_access.version import VERSION
from xnat_access.upload import _create_container_and_upload_file, _create_subject, _create_experiment


__version__ = VERSION


def session(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception:
            if self.session_is_open():
                raise
            self.open_session()
            return func(self, *args, **kwargs)

    return wrapper


class XNATClient:
    def __init__(self, xnat_base_url, username, password):
        self._username = username
        self._password = password
        self._url = xnat_base_url.rstrip('/')
        self._cookies = None
        atexit.register(self.close_session)

    def open_session(self):
        if self.session_is_open():
            raise Exception('Session already open.')

        r = requests.get(
            '{}/REST/JSESSION'.format(self._url),
            auth=(self._username, self._password)
        )
        r.raise_for_status()
        self._cookies = r.cookies

    def close_session(self):
        if not self.session_is_open():
            raise Exception('Session not open.')

        r = requests.delete(
            '{}/REST/JSESSION'.format(self._url),
            cookies=self._cookies
        )
        self._cookies = None
        r.raise_for_status()

    def session_is_open(self):
        if self._cookies is None:
            return False

        r = requests.get(
            '{}/REST/JSESSION'.format(self._url),
            cookies=self._cookies
        )
        try:
            r.raise_for_status()
        except Exception:
            self._cookies = None
            return False

        return True

    @session
    def get_request(self, rest_path, stream=None):
        r = requests.get(
            '{}/REST/{}'.format(self._url, rest_path.lstrip('/')),
            cookies=self._cookies,
            stream=stream
        )
        r.raise_for_status()
        return r

    @session
    def get_file(self, rest_path, encoding=None):
        encoding = encoding if encoding is not None else 'utf-8'
        r = self.get_request(rest_path, stream=True)
        return io.StringIO(r.content.decode(encoding))

    @session
    def get_json(self, rest_path):
        r = self.get_request('{}?format=json'.format(rest_path), stream=False)
        data = r.json()
        return data

    @session
    def get_result(self, rest_path):
        data = self.get_json(rest_path)
        return data['ResultSet']['Result']

    @session
    def download_file(self, rest_path, local_path):
        r = self.get_request(rest_path, stream=True)

        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)

    @session
    def put_request(self, rest_path, data=None):
        r = requests.put(
            '{}/REST/{}'.format(self._url, rest_path.lstrip('/')),
            cookies=self._cookies,
            data=data
        )
        r.raise_for_status()
        return r

    @session
    def upload_file(self, rest_path, local_path):
        with open(local_path, 'rb') as f:
            r = self.put_request('{}?inbody=true'.format(rest_path), data=f)
        return r

    @session
    def create_container_and_upload_file(
        self,
        local_path,
        project,
        subject,
        experiment,
        container_type,
        container,
        xsi_type,
        file_name,
        resource=None
    ):
        _create_container_and_upload_file(
            cookies=self._cookies,
            url=self._url,
            local_path=local_path,
            project=project,
            subject=subject,
            experiment=experiment,
            container_type=container_type,
            container=container,
            xsi_type=xsi_type,
            file_name=file_name,
            resource=resource
        )

    @session
    def create_subject(
        self,
        project,
        subject,
        group=None,
        weight=None,
        height=None,
        gender=None,
        yob=None,
        age=None,
        handedness=None
    ):
        _create_subject(
            cookies=self._cookies,
            url=self._url,
            project=project,
            subject=subject,
            group=group,
            weight=weight,
            height=height,
            gender=gender,
            yob=yob,
            age=age,
            handedness=handedness
        )

    @session
    def create_experiment(self, project, subject, experiment, xsi_type):
        _create_experiment(
            cookies=self._cookies,
            url=self._url,
            project=project,
            subject=subject,
            experiment=experiment,
            xsi_type=xsi_type
        )

    @session
    def delete_request(self, rest_path):
        r = requests.delete(
            '{}/REST/{}'.format(self._url, rest_path.lstrip('/')),
            cookies=self._cookies
        )
        r.raise_for_status()
        return r

    @session
    def post(self, path, data=None):
        r = requests.post(
            '{}/{}'.format(self._url, path.lstrip('/')),
            cookies=self._cookies,
            data=data
        )
        r.raise_for_status()
        return r
