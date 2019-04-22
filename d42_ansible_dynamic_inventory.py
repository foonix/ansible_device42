#!/usr/bin/env python

import argparse
from lib import get_conf, Ansible, Device42

try:
    import json
except ImportError:
    import simplejson as json

class Inventory():

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action='store_true')
        self.args = parser.parse_args()

        # Called with `--list`.
        if self.args.list:
            self.inventory = Inventory.get_groups()
        # Called with `--host [hostname]`.
        # If no groups or vars are present, return an empty inventory.
        else:
            self.inventory = Inventory.empty_inventory()

        print(json.dumps(self.inventory, indent=4))

    @staticmethod
    def get_groups():
        conf = get_conf()
        ansible = Ansible(conf)
        groups = ansible.get_grouping(Device42(conf).doql())
        groups['_meta'] = {'hostvars': {}}
        return groups

    @staticmethod
    def empty_inventory():
        return {'_meta': {'hostvars': {}}}

Inventory()
