import json
import logging
import os
from requests import HTTPError
from utils.constants import Constants
from utils.rest_client import RestClient

import logging
import os
import requests


class SchemaExporter:
    def __init__(self, base_url=None, ddx_cluster_id=None, ddx_cluster_token=None):
        # Ensure the base_url includes the scheme (https://)
        self.base_url = base_url or os.environ.get('CONTROLLER_BASE_URL') or Constants.DRIO_DEFAULT_BASE_ENDPOINT
        
        # Ensure the base_url starts with https:// or http:// and remove trailing slash
        if not self.base_url.startswith("http://") and not self.base_url.startswith("https://"):
            self.base_url = f"https://{self.base_url}"
        self.base_url = self.base_url.rstrip('/')  # Remove trailing slash

        self.ddx_cluster_id = ddx_cluster_id or os.environ.get('DDX_CLUSTER_ID')
        self.ddx_cluster_token = ddx_cluster_token or os.environ.get('DDX_CLUSTER_TOKEN')

        if not self.ddx_cluster_id or not self.ddx_cluster_token:
            raise ValueError("DDX Cluster ID and Token must be provided")

        self.rest_client = RestClient(self.base_url)
        self.headers = self.get_api_hdr(self.ddx_cluster_token)

    def export_schema(self, schema_detected, endpoint=None):
        # Build the full URL for schema export
        schema_endpoint = f'{self.base_url}/resources/ddx-clusters/{self.ddx_cluster_id}/schemas'
        try:
            logging.info("=======Started Schema Exporter======")
            response = self.send_schema_request(schema_detected, schema_endpoint)
            logging.info(f"Successfully exported schema to {schema_endpoint}: {response}, Response: {response}")
        except HTTPError as err:
            logging.error(f"HTTP error occurred while exporting schema: {err.response}")
            raise
        except Exception as e:
            logging.error(f"An error occurred while exporting schema: {e}")
            raise

    def send_schema_request(self, input_schemas, schema_endpoint):
        payload = input_schemas
        cluster_token = self.ddx_cluster_token
        headers = {
            'Accept': 'application/json; charset=utf-8',
            'Authorization': f'Bearer {cluster_token}',
            'Content-Type': 'application/json'
        }
        print(payload)
        # Disable SSL verification for testing environments if needed
        response = requests.request("PUT", schema_endpoint, headers=headers, data=payload, verify=False)
        try:
            response_json = response.json()
            logging.info(f"Response JSON: {json.dumps(response_json, indent=4)}")
        except ValueError:
            logging.warning("Response is not in JSON format")
        return response

    def get_api_hdr(self, token):
        if token is None:
            raise ValueError("Token must not be None")

        api_headers = {
            Constants.ACCEPT_HDR: Constants.APPLICATION_JSON_HDR_VALUE,
            Constants.AUTH_HDR: Constants.AUTH_HDR_VALUE.replace('{token}', token)
        }
        return api_headers
