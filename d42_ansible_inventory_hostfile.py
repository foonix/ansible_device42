import sys
import json
import requests
from lib import get_conf, Ansible, Device42

if __name__ == '__main__':
    conf = get_conf()
    ansible = Ansible(conf)
    groups = ansible.get_grouping(Device42(conf).doql())

    if ansible.write_inventory_file(groups) is True:
        print('[!] Done!')
    else:
        print('[!] Can\'t write to file')

    sys.exit()
