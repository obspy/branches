# -*- coding: utf-8 -*-
from StringIO import StringIO
from daemon import Daemon
from string import Template
from xml.etree import ElementTree as etree
import BaseHTTPServer
import cgi
import datetime
import os
import reporter
import sqlite3
import sys
import time
import urlparse


HOST_NAME = 'localhost'
PORT_NUMBER = 8000

# local path and files
path = os.path.dirname(reporter.__file__)

DB_NAME = os.path.join(path, "reporter.db")
PID_FILE = os.path.join(path, "reporter.pid")

# read static files
temp_css = open(os.path.join(path, 'templates', 'reporter.css')).read()
temp_index = open(os.path.join(path, 'templates', 'index.html')).read()
temp_datarow = open(os.path.join(path, 'templates', 'datarow.html')).read()

CREATE_SQL = """
    CREATE TABLE report (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp INTEGER,
        tests INTEGER,
        errors INTEGER,
        failures INTEGER,
        modules INTEGER,
        node TEXT,
        system TEXT,
        architecture TEXT,
        version TEXT,
        xml TEXT)
"""

INSERT_SQL = """
    INSERT INTO report (timestamp, tests, errors, failures, modules,
        system, architecture, version, xml, node) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

SELECT_ALL_SQL = """
    SELECT id, timestamp, tests, errors, failures, modules, system,
        architecture, version, xml, node 
    FROM report
    %s 
    ORDER BY timestamp DESC LIMIT 20
"""

SELECT_SQL = """
    SELECT id, timestamp, tests, errors, failures, modules, system,
        architecture, version, xml, node
    FROM report 
    WHERE id=?
"""

SELECT_ARCHS_SQL = """
    SELECT distinct(architecture)
    FROM report
    ORDER BY architecture
"""

SELECT_SYSTEMS_SQL = """
    SELECT distinct(system)
    FROM report
    ORDER BY system
"""

SELECT_VERSIONS_SQL = """
    SELECT distinct(version)
    FROM report
    ORDER BY version
"""

# create db connection
conn = sqlite3.connect(DB_NAME)

# create tables
try:
    conn.execute(CREATE_SQL)
except:
    pass

# fetch default filter
ARCHS = [i[0] for i in conn.execute(SELECT_ARCHS_SQL).fetchall()]
VERSIONS = [i[0] for i in conn.execute(SELECT_VERSIONS_SQL).fetchall()]
SYSTEMS = [i[0] for i in conn.execute(SELECT_SYSTEMS_SQL).fetchall()]


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def _stylesheet(self):
        self.wfile.write("""
        <style type='text/css'>%s</style>
        """ % temp_css)

    def _filter(self, id, items, qargs={}):
        url = "/?filter&amp;"
        for key, value in qargs.iteritems():
            if key == id:
                continue
            url += '%s=%s&amp;' % (key, value)
        out = '<ul class="filter">'
        if id in qargs:
            out += '  <li><a href="%s">all</a>&nbsp;</li>' % (url)
        else:
            out += '  <li><b>all</b>&nbsp;</li>'
        for item in items:
            out += "  <li>"
            if id in qargs and item == qargs[id]:
                out += "<b>%s</b>&nbsp;" % (item)
            else:
                out += '<a href="%s%s=%s">%s</a>&nbsp;' % (url, id, item, item)
            out += "  </li>"
        out += "</ul>"
        return out

    def do_GET(self):
        """
        Respond to a GET request.
        """
        if self.path.startswith('/?xml_id='):
            try:
                id = self.path[9:]
                result = conn.execute(SELECT_SQL, (id,))
                item = result.fetchone()
            except Exception, e:
                print e
                self.send_response(200)
                return
            self.send_response(200)
            self.send_header("Content-type", "text/xml")
            self.end_headers()
            self.wfile.write(item[9])
        elif self.path.startswith('/?id='):
            try:
                id = int(self.path[5:])
                result = conn.execute(SELECT_SQL, (id,))
                item = result.fetchone()
                root = etree.parse(StringIO(item[9])).getroot()
            except Exception, e:
                print e
                self.send_response(200)
                return
            self.send_response(200)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("<html>")
            self.wfile.write("<head>")
            self.wfile.write("<title>Report #%s</title>" % id)
            self._stylesheet()
            self.wfile.write("</head>")
            self.wfile.write("<body>")
            self.wfile.write("<a href='http://www.obspy.org'><img ")
            self.wfile.write(" style='float: right; border: none;' ")
            self.wfile.write(" src='http://obspy.org/www/obspy-logo.png' alt='ObsPy Logo' /></a>")
            self.wfile.write("<h1>Report #%s</h1>" % id)
            self.wfile.write("<p><a href='?id=%d' title='previous test'>&lt;&lt;&lt;</a>" % (id - 1))
            self.wfile.write(" &nbsp; <a href='?' title='start page'>Return to Overview</a> &nbsp; ")
            self.wfile.write(" <a href='?id=%d' title='next test'>&gt;&gt;&gt;</a></p>" % (id + 1))
            self.wfile.write("<h2>General Information</h2>")
            self.wfile.write("<ul>")
            timetaken = float(root.findtext('timetaken'))
            self.wfile.write("<li><b>Total Runtime</b> : %.3fs</li>" % (timetaken))
            self.wfile.write("<li><b>Report File</b> : <a href='/?xml_id=%s'>XML Document</a></li>" % (id))
            for item in root.find('platform')._children:
                tag = item.tag.replace('_',' ').title()
                self.wfile.write("<li><b>%s</b> : %s</li>" % (tag, item.text))
            self.wfile.write("</ul>")
            self.wfile.write("<h2>Dependencies</h2>\n")
            self.wfile.write("<ul>")
            children = root.find('dependencies')._children
            dependencies = dict([(c.tag, c) for c in children])
            for key in sorted(dependencies.keys()):
                self.wfile.write("<li><b>%s</b> : %s</li>" % (key, dependencies[key].text))
            self.wfile.write("</ul>")
            self.wfile.write("<h2>ObsPy</h2>\n")
            self.wfile.write("<table>\n")
            self.wfile.write("  <tr>\n")
            self.wfile.write("    <th>Module</th>\n")
            self.wfile.write("    <th>Version</th>\n")
            self.wfile.write("    <th>Errors/Failures</th>\n")
            self.wfile.write("    <th>Total / Average Runtime</th>\n")
            self.wfile.write("    <th>Tracebacks</th>\n")
            self.wfile.write("  </tr>\n")
            errlog = ""
            errid = 0
            children = root.find('obspy')._children
            modules = dict([(c.tag, c) for c in children])
            for key in sorted(modules.keys()):
                item = modules[key]
                errcases = ""
                self.wfile.write("  <tr>\n")
                version = item.findtext('installed')
                self.wfile.write("    <td>obspy.%s</td>" % (key))
                self.wfile.write("    <td>%s</td>" % (version))
                if item.find('tested') != None:
                    timetaken = float(item.findtext('timetaken'))
                    tests = int(item.findtext('tests'))
                    try:
                        avg = float(timetaken) / tests
                    except:
                        avg = 0
                    errors = 0
                    failures = 0
                    for sitem in item.find('errors')._children:
                        temp = sitem.text
                        temp = temp.replace('&' , '&amp;')
                        temp = temp.replace('<' , '&lt;')
                        temp = temp.replace('>' , '&gt;')
                        errlog += "<a name='%d'><h4>obspy.%s #%d</h4></a>" % (errid, key, errid)
                        errlog += "<pre>%s</pre>" % temp
                        errcases += "<a href='#%d'>#%d</a> " % (errid, errid)
                        errid += 1
                        errors += 1
                    for sitem in item.find('failures')._children:
                        temp = sitem.text
                        temp = temp.replace('&' , '&amp;')
                        temp = temp.replace('<' , '&lt;')
                        temp = temp.replace('>' , '&gt;')
                        errlog += "<a name='%d'><h4>obspy.%s #%d</h4></a>" % (errid, key, errid)
                        errlog += "<pre>%s</pre>" % temp
                        errcases += "<a href='#%d'>#%d</a> " % (errid, errid)
                        failures += 1
                        errid += 1
                    # error color
                    if errors > 0:
                        color = "error"
                    elif failures > 0:
                        color = "failure"
                    else:
                        color = "ok"
                    self.wfile.write("    <td class='%s'>%d of %d</td>" % (color, errors+failures, tests))
                    # time colors
                    if avg > 0.1:
                        color = "badtime"
                    elif avg > 0.05:
                        color = "slowtime"
                    else:
                        color = "oktime"
                    self.wfile.write("<td class='%s'>%.3fs / %.3fs</td>" % (color, timetaken, avg))
                    self.wfile.write("<td>%s</td>" % (errcases))
                else:
                    self.wfile.write("    <td colspan='3' style='color: grey'>Not tested</td>\n")
                self.wfile.write("  </tr>\n")
            self.wfile.write("</table>\n")
            self.wfile.write(errlog)
            try:
                log = root.findtext('install_log')
                log = unicode(log).encode("utf-8")
                if log != 'None':
                    self.wfile.write("<h2>Install Log</h2>")
                    self.wfile.write("<pre>%s</pre" % log)
            except Exception, e:
                print e
                pass
            self.wfile.write("</body></html>")
        else:
            # parse query
            query = urlparse.parse_qs(self.path)
            # filter
            filter = ''
            qargs = {}
            if 'system' in query and len(query['system']) == 1 and \
               query['system'][0] in SYSTEMS:
                qargs['system'] = query['system'][0]
                filter += "AND system='%s' " % qargs['system']
            if 'arch' in query and len(query['arch']) == 1 and \
                query['arch'][0] in ARCHS:
                    qargs['arch'] = query['arch'][0]
                    filter += "AND architecture='%s' " % qargs['arch']
            if 'version' in query and len(query['version']) == 1 and \
               query['version'][0] in VERSIONS:
                qargs['version'] = query['version'][0]
                filter += "AND version='%s' " % qargs['version']
            if filter:
                filter = 'WHERE' + filter[3:]
            # request data
            results = conn.execute(SELECT_ALL_SQL % filter)
            # write headers
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            # write page
            rows = ''
            temp = Template(temp_datarow)
            for item in results:
                data = {}
                data['id'] = item[0]
                data['datetime'] = datetime.datetime.fromtimestamp(item[1])
                data['tests'] = int(item[2])
                data['errors'] = errors = int(item[3])
                data['failures'] = failures = int(item[4])
                data['sum'] = sum = errors + failures
                data['modules'] = int(item[5])
                data['system'] = item[6]
                data['arch'] = item[7]
                data['version'] = item[8]
                data['node'] = item[10]
                if errors:
                    data['status'] = "error"
                elif failures:
                    data['status'] = "failure"
                else:
                    data['status'] = "ok"
                rows += temp.safe_substitute(**data)
            data = {}
            data['CSS'] = temp_css
            data['DATA'] = rows
            data['FILTER_SYSTEM'] = self._filter('system', SYSTEMS, qargs)
            data['FILTER_ARCH'] = self._filter('arch', ARCHS, qargs)
            data['FILTER_VERSION'] = self._filter('version', VERSIONS, qargs)
            out = Template(temp_index).safe_substitute(**data)
            self.wfile.write(out)

    def do_POST(self):
        """
        Respond to a POST request.
        """
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': self.headers['Content-Type'],
            })
        try:
            ts = int(form['timestamp'].value)
            xml_doc = form['xml'].value
            errors = int(form['errors'].value)
            failures = int(form['failures'].value)
            modules = int(form['modules'].value)
            tests = int(form['tests'].value)
            system = form['system'].value
            python_version = form['python_version'].value
            architecture = form['architecture'].value
            root = etree.parse(StringIO(xml_doc)).getroot()
            node = root.findtext('platform/node')
            conn.execute(INSERT_SQL, (ts, tests, errors, failures, modules, system,
                                      architecture, python_version, xml_doc, node))
            conn.commit()
        except Exception, e:
            self.send_response(500, str(e))
        else:
            self.send_response(200)


def run(self):
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME,
                                                     PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME,
                                                    PORT_NUMBER)

class MyDaemon(Daemon):
    run = run


if __name__ == "__main__":
    daemon = MyDaemon(PID_FILE)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'debug' == sys.argv[1]:
            run(1)
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart|debug" % sys.argv[0]
        sys.exit(2)
