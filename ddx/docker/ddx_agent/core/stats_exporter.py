import logging
import os

from requests import HTTPError

from utils.constants import Constants
from utils.rest_client import RestClient


class StatsExporter:
    def __init__(self, base_url=None, ddx_cluster_id=None, ddx_cluster_token=None):
        if base_url is None:
            self.base_url = os.environ.get('CONTROLLER_BASE_URL') or Constants.DRIO_DEFAULT_BASE_ENDPOINT
        if ddx_cluster_id is None:
            self.ddx_cluster_id = os.environ.get('DDX_CLUSTER_ID')
        if ddx_cluster_token is None:
            self.ddx_cluster_token = os.environ.get('DDX_CLUSTER_TOKEN')

        self.rest_client = RestClient(f'https://{self.base_url}')
        self.headers = get_api_hdr(self.ddx_cluster_token)

    def export(self, stats, ep):
        # stats_endpoint = f'resources/ddx-clusters/{self.ddx_cluster_id}/datasets'
        try:
            _ = self.rest_client.put(ep, stats, headers=self.headers, verify=False)
        except HTTPError as err:
            logging.error(err.response.text)
        except Exception as e:
            logging.error(e)


def get_api_hdr(token):
    api_headers = {
        Constants.ACCEPT_HDR: Constants.APPLICATION_JSON_HDR_VALUE,
        Constants.AUTH_HDR: Constants.AUTH_HDR_VALUE.replace('{token}', token)
    }
    return api_headers
