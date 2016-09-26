# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2001-2014 Micronaet SRL (<http://www.micronaet.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import os
import sys
import logging
import openerp
import openerp.netsvc as netsvc
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)

class SsccCode(orm.Model):
    """ Model name: SsccCode
    """
    
    _name = 'sscc.code'
    _description = 'SSCC Code'
    
    _columns = {
        'name': fields.char(
            'Counter', size=64, required=True,
              
            ),
        # Function complete code
        # TODO 1st char??    
        }

class SsccInvoice  (orm.Model):
    """ Model name: SsccInvoice
    """
    
    _name = 'sscc.invoice'
    _description = 'SSCC Invoice'
    
    _columns = {
        'name': fields.char('Number', size=15, required=True),
        'date': fields.date('Date'),
        'year': fields.char('Year', size=4),
        'journal': fields.char('Journal', size=64, required=False, 
            readonly=False),   
        'partner_id': fields.many2one(
            'res.partner', 'Partner'), 
        # Function complete code
        # TODO 1st char??    
        }
        
class SsccInvoiceLine  (orm.Model):
    """ Model name: SsccInvoiceLine
    """
    
    _name = 'sscc.invoice.line'
    _description = 'SSCC Invoice Line'
    
    _columns = {
        'name': fields.char('Description', size=64),
        'code': fields.char('Code', size=20),
        'uom': fields.char('UOM', size=2), 
        'quantity': fields.float('Quantity', digits=(16, 2)), 
        'invoice_id': fields.many2one('sscc.invoice', 'Invoice'), 
        # Function complete code
        # TODO 1st char??    
        }
        

        
        

        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
