import imp
import os
import sys
import requests
try:
    import json
except ImportError:
    import simplejson as json

def get_conf():
    try:
        conf = imp.load_source('conf', 'conf').__dict__
        if 'D42_SKIP_SSL_CHECK' in conf and conf['D42_SKIP_SSL_CHECK']:
            requests.urllib3.disable_warnings(requests.urllib3.exceptions.InsecureRequestWarning)
    except FileNotFoundError:
        if 'D42_SKIP_SSL_CHECK' in os.environ and os.environ['D42_SKIP_SSL_CHECK'] == 'True':
            requests.urllib3.disable_warnings(requests.urllib3.exceptions.InsecureRequestWarning)

        if 'D42_URL' not in os.environ:
            print('Please set D42_URL environ.')
            sys.exit()

        if 'D42_USER' not in os.environ:
            print('Please set D42_USER environ.')
            sys.exit()

        if 'D42_PWD' not in os.environ:
            print('Please set D42_PWD environ.')
            sys.exit()

        if 'GROUP_BY_QUERY' not in os.environ:
            print('Please set GROUP_BY_QUERY environ.')
            sys.exit()

        if 'GROUP_BY_FIELD' not in os.environ:
            print('Please set GROUP_BY_FIELD environ.')
            sys.exit()

        if 'GROUP_BY_REFERENCE_FIELD' not in os.environ:
            print('Please set GROUP_BY_REFERENCE_FIELD environ.')
            sys.exit()

        conf = {
            'D42_URL': os.environ['D42_URL'],
            'D42_USER': os.environ['D42_USER'],
            'D42_PWD': os.environ['D42_PWD'],
            'GROUP_BY_QUERY': os.environ['GROUP_BY_QUERY'],
            'GROUP_BY_FIELD': os.environ['GROUP_BY_FIELD'],
            'GROUP_BY_REFERENCE_FIELD': os.environ['GROUP_BY_REFERENCE_FIELD']
        }
    except ImportError as import_error:
        print("Failed to parse conf file:", type(import_error).__name__, str(import_error))
        sys.exit()
    return conf

class Device42:

    def __init__(self, conf):
        self.conf = conf
        self.password = self.conf['D42_PWD']
        self.username = self.conf['D42_USER']
        self.base_url = self.conf['D42_URL']
        self.query = self.conf['GROUP_BY_QUERY']

    def fetcher(self, url, query):
        response = requests.post(url, data={
            'query': query,
            'output_type': 'json'
        }, auth=(self.username, self.password), verify=False)
        return response.text

    def doql(self):
        url = self.base_url + '/services/data/v1.0/query/'
        doql_response = json.loads(self.fetcher(url, self.query))

        if(isinstance(doql_response, dict) and 'error' in doql_response):
            print('DOQL error:', doql_response['error'])
            sys.exit()

        return doql_response

class Ansible:

    def __init__(self, conf):
        self.conf = conf

    def get_grouping(self, objects):
        groups = {}
        for object_ in objects:
            if self.conf['SPLIT_GROUP_BY_COMMA']:
                for group in object_[self.conf['GROUP_BY_FIELD']].split(','):
                    if group not in groups:
                        groups[group] = []
                    groups[group].append(object_[self.conf['GROUP_BY_REFERENCE_FIELD']])
            else:
                if object_[self.conf['GROUP_BY_FIELD']] not in groups:
                    groups[object_[self.conf['GROUP_BY_FIELD']]] = []
                groups[object_[self.conf['GROUP_BY_FIELD']]].append(
                    object_[self.conf['GROUP_BY_REFERENCE_FIELD']]
                )

        return groups

    @staticmethod
    def write_inventory_file(groups):

        with open("hosts", "w") as hosts_file:
            # Ungrouped devices must be outside of ini block
            if None in groups:
                for device in groups[None]:
                    hosts_file.write(device + '\n')

            for group in groups:
                if group is None:
                    continue
                hosts_file.write('[' + group + ']\n')
                for device in groups[group]:
                    hosts_file.write(device + '\n')
                hosts_file.write('\n')

        return True
