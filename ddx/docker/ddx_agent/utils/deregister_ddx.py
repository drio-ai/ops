import os

from utils.rest_client import RestClient


def _get_ddx_reg_params():
    return {
        'base_url': os.environ.get('CONTROLLER_BASE_URL'),
        'account_id': os.environ.get('ACCOUNT_ID'),
        'ou_id': os.environ.get('OU_ID'),
        'ddx_cluster_id': os.environ.get('DDX_CLUSTER_ID'),
        'ddx_name': os.environ.get('DDX_INSTANCE_NAME'),
        'cluster_token': os.environ.get('DDX_CLUSTER_TOKEN')
    }


def deregister_ddx(d_id):
    # de-register the DDX instance
    reg_params = _get_ddx_reg_params()
    r_client = RestClient(f'https://{reg_params.get("base_url")}')
    deregister_api = f'resources/ddx-instances/{d_id}'
    payload = {
        "cluster_id": reg_params.get('ddx_cluster_id'),
        "token": reg_params.get('cluster_token')
    }
    r_client.delete(deregister_api, payload, verify=False)


if __name__ == '__main__':
    ACCOUNT_ID = os.environ.get('ACCOUNT_ID')
    OU_ID = os.environ.get('OU_ID')
    DDX_CLUSTER_ID = os.environ.get('DDX_CLUSTER_ID')
    rest_client = RestClient(f"https://{os.environ.get('CONTROLLER_BASE_URL')}")
    get_url = f'resources/accounts/{ACCOUNT_ID}/ous/{OU_ID}' \
              f'/ddx-clusters/{DDX_CLUSTER_ID}/ddx-instances?offset=0&limit=200'
    token = os.environ.get('AUTH_TOKEN')
    headers = {
        'accept': 'application/json',
        'Authorization': token
    }

    while True:
        res = rest_client.get(get_url, headers=headers, verify=False)
        if not res or not res.json():
            break
        for d in res.json():
            ddx_id = d.get('id')
            print(f'Removing DDX Instance with Id: {ddx_id}')
            deregister_ddx(ddx_id)

