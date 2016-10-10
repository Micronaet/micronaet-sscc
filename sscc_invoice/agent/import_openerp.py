#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# use: partner.py file_csv_to_import

# Modules required:
import xmlrpclib
import csv
import sys
import ConfigParser
import os

folder = sys.argv[1]
pipe_material = folder[:2] # first 2 char are symbol

path = os.path.expanduser(os.path.join(
    '~/etl/Access/import/data', folder))
cfg_file = os.path.expanduser('~/etl/Access/import/openerp.cfg')

config = ConfigParser.ConfigParser()
config.read([cfg_file])
dbname = config.get('dbaccess', 'dbname')
user = config.get('dbaccess', 'user')
pwd = config.get('dbaccess', 'pwd')
server = config.get('dbaccess', 'server')
port = config.get('dbaccess', 'port')   # verify if it's necessary: getint

sock = xmlrpclib.ServerProxy(
    'http://%s:%s/xmlrpc/common' % (server, port), allow_none=True)
uid = sock.login(dbname, user, pwd)
sock = xmlrpclib.ServerProxy(
    'http://%s:%s/xmlrpc/object' % (server, port), allow_none=True)

sock.execute(dbname, uid, pwd, 'sscc.invoice', 'import_invoice_csv')

