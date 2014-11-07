mdb-collectd-plugin
===================

Usage:

<Plugin rrdtool>
    DataDir "/home/alex/mdb/rrd"
</Plugin>

<LoadPlugin "python">
  Globals true
</LoadPlugin>

<Plugin python>
  ModulePath "/home/alex"
  Import "mdb_plugin"
  <Module mdb_plugin>
    MonitoringEndpoint "http://192.168.0.102:8480"
    ProjectsToMonitor "default_tenant" "test"
  </Module>
</Plugin>
