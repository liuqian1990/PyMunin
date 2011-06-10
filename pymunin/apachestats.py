#!/usr/bin/python
#
# apachestats - Munin Plugin to monitor stats for Apache Web Server.
#
# Requirements
#   - Access to Apache Web Server server-status page.
# 
#
# Wild Card Plugin - No
#
#
# Multigraph Plugin - Graph Structure
#    - apache_access
#    - apache_bytes
#    - apache_workers
#
#    
# Environment Variables
#   host:           Apache Web Server Host. (Default: 127.0.0.1)
#   port:           Apache Web Server Port. (Default: 8080, SSL: 8443)
#   user:           User in case authentication is required for access to server-status.
#   password:       User in case authentication is required for access to server-status.
#   ssl:            Use SSL if yes. (Default: no)
#   include_graphs: Comma separated list of enabled graphs. (All graphs enabled by default.)
#   exclude_graphs: Comma separated list of disabled graphs.
#
#   Example:
#     [apachestats]
#         env.exclude_graphs apache_access,apache_load
#
#
# Munin  - Magic Markers
#%# family=manual
#%# capabilities=noautoconf nosuggest

__author__="Ali Onur Uyar"
__date__ ="$Dic 29, 2010 10:58:22 PM$"

import sys
from pymunin import MuninGraph, MuninPlugin, muninMain
from pysysinfo.apache import ApacheInfo


class MuninApachePlugin(MuninPlugin):
    """Multigraph Munin Plugin for monitoring Apache Web Server.

    """
    plugin_name = 'apachestats'
    isMultigraph = True

    def __init__(self, argv = (), env = {}):
        """Populate Munin Plugin with MuninGraph instances.
        
        @param argv: List of command line arguments.
        @param env:  Dictionary of environment variables.
        
        """
        MuninPlugin.__init__(self, argv, env)
        
        self._host = self._env.get('host')
        self._port = self._env.get('port')
        self._user = self._env.get('user')
        self._password = self._env.get('password')
        self._ssl = self._env.get('ssl', '').lower() in ('yes', 'on') 
        
        if self.graphEnabled('apache_access'):
            graph = MuninGraph('Apache Web Server - Throughput (Requests / sec)', 'Apache',
                info='Throughput in Requests per second for Apache Web Server.',
                args='--base 1000 --lower-limit 0')
            graph.addField('reqs', 'reqs', draw='LINE2', type='DERIVE', min=0,
                info="Requests per second.")
            self.appendGraph('apache_access', graph)
        
        if self.graphEnabled('apache_bytes'):
            graph = MuninGraph('Apache Web Server - Througput (bytes/sec)', 'Apache',
                info='Throughput in bytes per second for Apache Web Server.',
                args='--base 1024 --lower-limit 0')
            graph.addField('bytes', 'bytes', draw='LINE2', type='DERIVE', min=0)
            self.appendGraph('apache_bytes', graph)
                
        if self.graphEnabled('apache_workers'):
            graph = MuninGraph('Apache Web Server - Workers', 'Apache',
                info='Worker utilization stats for Apache Web server.',
                args='--base 1000 --lower-limit 0')
            graph.addField('busy', 'busy', draw='AREASTACK', type='GAUGE',
                info="Number of busy workers.")
            graph.addField('idle', 'idle', draw='AREASTACK', type='GAUGE',
                info="Number of idle workers.")
            graph.addField('max', 'max', draw='LINE2', type='GAUGE',
                info="Maximum number of workers permitted.",
                colour='FF0000')
            self.appendGraph('apache_workers', graph)
        
    def retrieveVals(self):
        """Retrive values for graphs."""
        apacheInfo = ApacheInfo(self._host, self._port,
                                self._user, self._password, self._ssl)
        stats = apacheInfo.getServerStats()
        if self.graphEnabled('apache_access'):
            self.setGraphVal('apache_access', 'reqs', stats['Total Accesses'])
        if self.graphEnabled('apache_bytes'):
            self.setGraphVal('apache_bytes', 'bytes', stats['Total kBytes'] * 1000)
        if self.graphEnabled('apache_workers'):
            self.setGraphVal('apache_workers', 'busy', stats['BusyWorkers'])
            self.setGraphVal('apache_workers', 'idle', stats['IdleWorkers'])
            self.setGraphVal('apache_workers', 'max', stats['MaxWorkers'])


if __name__ == "__main__":
    sys.exit(muninMain(MuninApachePlugin))
