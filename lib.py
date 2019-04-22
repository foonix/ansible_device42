try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import csv
import base64
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
        if 'D42_SKIP_SSL_CHECK' in conf and conf['D42_SKIP_SSL_CHECK'] == True:
            requests.urllib3.disable_warnings(requests.urllib3.exceptions.InsecureRequestWarning)
    except:
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
    return conf

class Device42:

    def __init__(self, conf):
        self.conf = conf
        self.password = self.conf['D42_PWD']
        self.username = self.conf['D42_USER']
        self.base_url = self.conf['D42_URL']
        self.query = self.conf['GROUP_BY_QUERY']

    def fetcher(self, url, query):
        headers = {
            'Authorization': 'Basic ' + base64.b64encode((self.username + ':' + self.password).encode('utf-8')).decode('utf-8'),
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(url, data={
            'query': query,
            'header': 'yes'
        }, headers=headers, verify=False)
        return response.text

    def doql(self):
        url = self.base_url + '/services/data/v1.0/query/'
        return self.get_list_from_csv(self.fetcher(url, self.query))

    @staticmethod
    def get_list_from_csv(text):
        csv_buffer = StringIO(text)
        list_ = []
        dict_reader = csv.DictReader(csv_buffer, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True, dialect='excel')
        for item in dict_reader:
            list_.append(item)

        return list_


class Ansible:

    def __init__(self, conf):
        self.conf = conf

    def get_grouping(self, objects):
        groups = {}
        for object_ in objects:
            try:
                if self.conf['SPLIT_GROUP_BY_COMMA']:
                    for group in object_[self.conf['GROUP_BY_FIELD']].split(','):
                        if group not in groups:
                            groups[group] = []
                        groups[group].append(object_[self.conf['GROUP_BY_REFERENCE_FIELD']])
                else:
                    if object_[self.conf['GROUP_BY_FIELD']] not in groups:
                        groups[object_[self.conf['GROUP_BY_FIELD']]] = []
                    groups[object_[self.conf['GROUP_BY_FIELD']]].append(object_[self.conf['GROUP_BY_REFERENCE_FIELD']])
            except Exception:
                print(object_)
                sys.exit()
        return groups

    @staticmethod
    def write_inventory_file(groups):

        hosts_file = open("hosts", "w")

        for group in groups:
            hosts_file.write('[' + group + ']\n')
            for device in groups[group]:
                hosts_file.write(device + '\n')
            hosts_file.write('\n')

        hosts_file.close()

        return True
