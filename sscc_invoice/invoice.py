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
    
    # Import function:
    def import_invoice_csv(self, cr, uid, ids, context=None):
        ''' Import csv file
        '''
        # Pool used:
        line_pool = self.pool.get('sscc.invoice.line')
        
        # Initial setup_
        filename = '/home/thebrush/etl/fattura.csv' # TODO
        
        header = True
        invoice_id = False
        for line in open(filename, 'r'):
            # -----------------------------------------------------------------     
            # Header data:            
            # -----------------------------------------------------------------     
            if header:               
                header = False                

                # Fields:
                number_invoice = line[0:6] # 6
                date_invoice = line[6:16] # 10
                partner_code = '' # TODO
                
                # Calculated fields:
                partner_id = False # TODO
               
                # TODO check number invoice first
                
                # Create header
                invoice_id = self.create(cr, uid, {
                    'name': number_invoice,
                    'date': date_invoice,
                    'year': date_invoice[:4],                    
                    'partner_id': partner_id,
                    #'journal':
                    }, context=context)
                        
            # -----------------------------------------------------------------     
            # Row data:
            # -----------------------------------------------------------------     
            # Fields:
            order_number = line[16:22] # 6
            order_date = line[22:32] # 10
            code = line[32:48] # 16
            description = line[1:72]
            uom = line[]
            currency = line[]            
            price = line[1:10] # 10
            duty_code = line[] # 8
            #sscc = line[] # 18
            quantity = line[]
            q_x_pack = line[]
            parcel = line[]
            net_weight = line[]
            weight = line[]
            lot = line[]
            deadline = line[]
            country_origin = line[]
            country_from = line[] # Italy
            #duty_ok = line[]
            #mnr_number = line[]
            #sanitary = line[]
            #sanitary_date = line[]
            #extra_code = line[]
            #sif = line[]
            
            line_pool.create(cr, uid, {
                'invoice_id': invoice_id,
                'name': description,
                'code': code,
                'uom': uom,
                'quantity': quantity,
                'order_date': order_date,
                'order_number': order_number,                 
                 
                 }, context=context)
               
        return True
        
    _columns = {
        'name': fields.char('Number', size=15, required=True),
        'date': fields.date('Date'),
        'year': fields.char('Year', size=4),
        'journal': fields.char('Journal', size=64),   
        'partner_id': fields.many2one('res.partner', 'Partner'),         
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
        'order_date': fields.date('Order date'),
        'order_number': fields.char('Order number', size=15), 
        'sscc_id': fields.many2one('sscc.code', 'SSCC code'), 
        
        
        # Function complete code
        # TODO 1st char??    
        }
        
class SsccInvoice  (orm.Model):
    """ Model name: SsccInvoice
    """
    
    _inherit = 'sscc.invoice'
    
    _columns = {
        'line_ids': fields.one2many('sscc.invoice.line', 'invoice_id', 'Line'), 
        }

        
        

        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
