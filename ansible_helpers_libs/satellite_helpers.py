import re
import ConfigParser
import shlex
import os
import json
import xmlrpclib


def getserver():
    with open('/etc/sysconfig/rhn/up2date', 'r') as up2date_handle:
        up2date_config = up2date_handle.read()
        return "%s/rpc/api" % re.match('.*\n\s*serverURL=(.*?)XMLRPC', up2date_config).group(0)


def create_connection(url, username, password, verbose=0):
    server_con = xmlrpclib.ServerProxy(uri=url, verbose=verbose)
    auth = server_con.auth.login(username, password)
    return auth, server_con


def get_json(sat_connection, sat_auth, groups):
    result = {'_meta': {'hostvars': dict()}}

    for group in groups:
        hosts = [i['name'] for i in
                 sat_connection.systemgroup.listSystemsMinimal(sat_auth, group)]
        result[group] = {
            'hosts': hosts,
        }

        for host in hosts:
            result['_meta']['hostvars'][host] = {}
    return json.dumps(result)


def get_config(conf_file=None):
    if not conf_file:
        conf_file = os.getenv('SATELANS_CONFIG')

    conf_obj = ConfigParser.RawConfigParser()
    conf_obj.read(conf_file)
    return {
        'url': conf_obj.get('main', 'url'),
        'username': conf_obj.get('main', 'username'),
        'password': conf_obj.get('main', 'password'),
        'groups': shlex.split(conf_obj.get('main', 'groups')),
        }


