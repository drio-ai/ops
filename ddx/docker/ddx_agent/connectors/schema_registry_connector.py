import os

from utils.rest_client import RestClient

LOCAL_SR = 'http://localhost:8081'


class SRConnect:
    def __init__(self, sr_endpoint):
        headers = {'Accept': 'application/vnd.schemaregistry.v1+json, application/vnd.schemaregistry+json,'
                             ' application/json'}
        self.rest_client = RestClient(sr_endpoint or LOCAL_SR, headers=headers)

    def get_subject_list(self):
        return self.rest_client.get('subjects').json()

    def get_schema_versions(self, subject):
        return self.rest_client.get(f'/subjects/{subject}/versions').json()

    def get_schema(self, subject, version):
        return self.rest_client.get(f'/subjects/{subject}/versions/{version}/schema').json()

    def get_schema_stats(self):
        sr_subjects = self.get_subject_list()
        sub_vers = {sub: self.get_schema_versions(sub) for sub in sr_subjects}
        schemas = {}
        for sub, vers in sub_vers.items():
            if sub not in schemas:
                schemas[sub] = {}

            for v in vers:
                schemas[sub].update({str(v): self.get_schema(sub, v)})
        return schemas
