import requests
import json
from urllib.parse import urljoin

from singleton_decorator import singleton


@singleton
class RestClient:
    def __init__(self, base_url, **kwargs):
        self.base_url = base_url
        self.default_headers = {'Content-Type': 'application/json; charset=utf-8'}
        self.default_timeout = kwargs.get('timeout', 10)

    def get(self, url, params=None, **kwargs):
        raw = kwargs.pop('raw', False)
        if kwargs.get('headers') is None or type(kwargs['headers']) != dict:
            kwargs['headers'] = self.default_headers
        else:
            kwargs['headers'].update(self.default_headers)

        kwargs['timeout'] = kwargs.get('timeout', self.default_timeout)
        response = requests.get(urljoin(self.base_url, url), params, **kwargs)
        if not raw:
            response.raise_for_status()

        return response

    def post(self, url, payload, **kwargs):
        raw = kwargs.pop('raw', False)
        if kwargs.get('headers') is None or type(kwargs['headers']) != dict:
            kwargs['headers'] = self.default_headers
        else:
            kwargs['headers'].update(self.default_headers)

        kwargs['timeout'] = kwargs.get('timeout', self.default_timeout)
        response = requests.post(urljoin(self.base_url, url), data=json.dumps(payload), **kwargs)
        if not raw:
            response.raise_for_status()

        return response

    def put(self, url, payload, **kwargs):
        raw = kwargs.pop('raw', False)
        if kwargs.get('headers') is None or type(kwargs['headers']) != dict:
            kwargs['headers'] = self.default_headers
        else:
            kwargs['headers'].update(self.default_headers)

        kwargs['timeout'] = kwargs.get('timeout', self.default_timeout)
        response = requests.put(urljoin(self.base_url, url), data=json.dumps(payload), **kwargs)
        if not raw:
            response.raise_for_status()

        return response

    def delete(self, url, payload, **kwargs):
        raw = kwargs.pop('raw', False)
        if kwargs.get('headers') is None or type(kwargs['headers']) != dict:
            kwargs['headers'] = self.default_headers
        else:
            kwargs['headers'].update(self.default_headers)

        kwargs['timeout'] = kwargs.get('timeout', self.default_timeout)
        response = requests.delete(urljoin(self.base_url, url), data=json.dumps(payload), **kwargs)
        if not raw:
            response.raise_for_status()

        return response
