import configparser
import logging
import os
import netifaces

from requests import HTTPError

from utils.constants import Constants
from utils.file_utils import write_config_to_file, process_config_json
from utils.rest_client import RestClient
from core.stats_exporter import get_api_hdr


class Drio:
    def __init__(self, ddx_id, ddx_name, service_provider):
        self.ddx_id = ddx_id
        self.service_provider = service_provider
        self.ddx_name = ddx_name

    def register_ddx(self):
        # Register the DDX instance
        reg_params = self.get_ddx_reg_params()
        rest_client = RestClient(f'https://{reg_params.get("base_url")}')
        register_api = f'resources/ddx-instances'
        ip_addr = self.get_instance_ip_addr()
        payload = {
            "id": self.ddx_id,
            "name": reg_params.get('ddx_name'),
            "cluster_id": reg_params.get('ddx_cluster_id'),
            "ipaddress": ip_addr,
            "token": reg_params.get('cluster_token')
        }
        logging.info(register_api)
        logging.info(payload)

        try:
            hdr = {'accept': 'application/json'}
            response = rest_client.post(register_api, payload, headers=hdr, verify=False, timeout=10)
            logging.info(response.json())
            return response.json()
        except HTTPError as err:
            if err.response.status_code == 400:
                return {}
            else:
                logging.error(err.response.text)
                raise

    def deregister_ddx(self, ddx_id=None):
        logging.info('deregister_ddx called')
        # de-register the DDX instance
        reg_params = self.get_ddx_reg_params()
        rest_client = RestClient(f'https://{reg_params.get("base_url")}')
        deregister_api = f'resources/ddx-instances/{ddx_id or self.ddx_id}'
        payload = {
            "cluster_id": reg_params.get('ddx_cluster_id'),
            "token": reg_params.get('cluster_token')
        }
        rest_client.delete(deregister_api, payload, verify=False, timeout=10)

    @staticmethod
    def pull_config(filters=None):
        cluster_id = os.environ.get('DDX_CLUSTER_ID')
        config_endpoint = f'resources/ddx-clusters/{cluster_id}/configuration'
        base_ep = os.environ.get('CONTROLLER_BASE_URL') or Constants.DRIO_DEFAULT_BASE_ENDPOINT
        try:
            headers = get_api_hdr(os.environ.get('DDX_CLUSTER_TOKEN'))
            rest_client = RestClient(f'https://{base_ep}')
            response = rest_client.get(config_endpoint, None, headers=headers, verify=False)
            config_json = response.json()
            logging.info(f'obtained config {config_json}')
            config = process_config_json(config_json, filters)
            write_config_to_file(config, Constants.PROPERTIES_FILE_NAME)
        except HTTPError as err:
            logging.error(err.response.text)
        except Exception as e:
            logging.error(e)

    def get_ddx_reg_params(self):
        return {
            'base_url': os.environ.get('CONTROLLER_BASE_URL') or Constants.DRIO_DEFAULT_BASE_ENDPOINT,
            'ddx_name': self.ddx_name,
            'ddx_cluster_id': os.environ.get('DDX_CLUSTER_ID'),
            'cluster_token': os.environ.get('DDX_CLUSTER_TOKEN')
        }

    def get_instance_ip_addr(self):
        if self.service_provider.lower() == 'aws':
            try:
                rc = RestClient(f'http://{Constants.AWS_META_SERVER}/latest/meta-data/')
                ec2_instance_ip = rc.get('local-ipv4', headers={'Content-Type': 'text/plain'}).text
                return ec2_instance_ip
            except Exception:
                local_ip = True
        else:
            local_ip = True

        if local_ip:
            ip_addrs = []
            interfaces = netifaces.interfaces()
            addrs = [netifaces.ifaddresses(intf) for intf in interfaces if intf != 'lo0']
            for addr in addrs:
                if addr and netifaces.AF_INET in addr:
                    af_nets = addr[netifaces.AF_INET]
                    for net in af_nets:
                        if net['addr'] != '127.0.0.1':
                            ip_addrs.append(net['addr'])

            return ip_addrs[0] if ip_addrs else None
