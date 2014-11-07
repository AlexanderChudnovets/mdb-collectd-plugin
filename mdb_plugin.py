import random

import collectd
import gevent
import requests


MDB_ENDPOINT = 'http://127.0.0.1:8480'
PROJECTS = ['default_tenant']


def get_headers():
    return {"Content-type": "application/json"}


def get_table_info(project, table):
    url = "%s/v1/%s/monitoring/tables/%s" % (MDB_ENDPOINT, project, table)
    data = requests.get(url, headers=get_headers()).json()
    result = { "name": table }
    result.update(data)
    return result


def get_tables(project):
    url = "%s/v1/%s/monitoring/tables" % (MDB_ENDPOINT, project)
    data = requests.get(url, headers=get_headers()).json()
    
    return [table["href"] for table in data["tables"]]


def get_project_info(project):
    jobs = [gevent.spawn(get_table_info, project, table) for table
            in get_tables(project)]
    gevent.joinall(jobs, timeout=20)
    return {
        "name": project,
        "tables": [job.value for job in jobs]
    }


def get_info():
    return [get_project_info(project) for project in PROJECTS]


def configure_callback(conf):
    global MDB_ENDPOINT, PROJECTS
    for node in conf.children:
        if node.key == 'MonitoringEndpoint':
            MDB_ENDPOINT = node.values[0]
        elif node.key == 'ProjectsToMonitor':
            PROJECTS = node.values
        else:
            collectd.warning('mdb_monitoring plugin: Unknown config key: %s.'
                             % node.key)


def get_gauge(data):
    if not data:
        return 0
    if isinstance(data, float):
        return int(data)
    return data


def dispatch_values(project):
    for table in project["tables"]:
        val = collectd.Values(plugin='mdb-monitoring')
        val.type = 'gauge'
        val.type_instance = '%s-%s-item_count' % (project["name"], table["name"])
        val.values = [get_gauge(table["item_count"])]
        val.dispatch()

        val = collectd.Values(plugin='mdb-monitoring')
        val.type = 'gauge'
        val.type_instance = '%s-%s-size' % (project["name"], table["name"])
        val.values = [get_gauge(table["size"])]
        val.dispatch()

  
def read_callback():
    info = get_info()
    for project in info:
        dispatch_values(project)


collectd.register_config(configure_callback)
collectd.register_read(read_callback)
