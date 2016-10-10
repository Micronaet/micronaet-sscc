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
    
    # -------------------------------------------------------------------------
    # Utility:
    # -------------------------------------------------------------------------
    def _sscc_check_digit(self, fixed):
        ''' Generate check digit and return
        '''
        tot = 0
        pos = 0
        
        for c in fixed:
            pos+=1
            number = int(c)
            if pos % 2 == 0 :
                tot += number
            else:
                tot += number*3
        
        remain = tot % 10
        if remain:
            return 10 - remain 
        else: 
            return 0
    
    def _generate_sscc_code_with_check(self, cr, uid, context=None):
        ''' Generate partial code with counter and add check digit
        '''
        fixed = self.pool.get('ir.sequence').get(
            cr, uid, 'sscc.code.number')
            
        return '%s%s' % (fixed, self._sscc_check_digit(fixed))
            
        
    def _get_sscc_code(self, cr, uid, ids, fields, args, context=None):
        ''' Fields function for calculate 
        '''
        res = {}
        for item in self.browse(cr, uid, ids, context=context):
            res[item.id] = '%s%s' % (item.code_type, item.name)
        return res
        
    def _get_total_line(self, cr, uid, ids, fields, args, context=None):
        ''' Fields function for calculate 
        '''    
        res = {}
        for code in self.browse(cr, uid, ids, context=context):
            res[code.id] = len(code.line_ids)
        return res
            
    _columns = {
        'name': fields.char('Counter', size=18, required=True),  
        'create_date': fields.date('Create date', readonly=True),
        'invoice_id': fields.many2one('sscc.invoice', 'Invoice'), 
        'total_line': fields.function(_get_total_line, method=True, 
            type='integer', string='Total line', 
            store=False, readonly=True), 
        
        #'code_type': fields.selection([
        #    ('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'),
        #    ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'),
        #    ('8', '8'), ('9', '9'),
        #    ], 'Code Type'),
        #'code': fields.function(_get_sscc_code, method=True, 
        #    type='string', string='SSCC Code', store=False), 
            
        # Function complete code
        # TODO 1st char??    
        }
        
    _defaults = {
        'name': lambda s, cr, uid, ctx: s._generate_sscc_code_with_check(
            cr, uid, context=ctx),
        }    

class SsccInvoice  (orm.Model):
    """ Model name: SsccInvoice
    """    
    _name = 'sscc.invoice'
    _description = 'SSCC Invoice'
             
    # -------------------------------------------------------------------------         
    # Button:
    # -------------------------------------------------------------------------         
    # Workflow-like button:
    def state_assigned(self, cr, uid, ids, context=None):
        ''' Set invoice as assigned, check all code
        '''
        assert len(ids) == 1, 'Works only with one record a time'
        
        invoice_proxy = self.browse(cr, uid, ids, context=context)[0]
        for line in invoice_proxy.line_ids:
            if not line.sscc_id:
                raise osv.except_osv(
                    _('Error'), 
                    _('Not all line has SSCC code!'),
                    )
        return self.write(cr, uid, ids, {'state': 'assigned'}, context=context)
            
    def state_closed(self, cr, uid, ids, context=None):
        ''' Set invoice as assigned, check all code
        '''
        assert len(ids) == 1, 'Works only with one record a time'

        return self.write(cr, uid, ids, {'state': 'closed'}, context=context)
    
    def manage_line_in_kanban(self, cr, uid, ids, context=None):
        ''' Open kanban for SSCC code association 
        '''
        if context is None:
            context = {}
        model_pool = self.pool.get('ir.model.data')
        view_id = model_pool.get_object_reference(cr, uid,
            'sscc_invoice', 'view_sscc_invoice_line_kanban')[1]
        context['default_invoice_id'] = ids[0]
        context['invoice_embedded'] = True
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Manage SSCC code'),
            'view_type': 'form',
            'view_mode': 'kanban,tree,form',
            'res_model': 'sscc.invoice.line',
            'view_id': view_id, # False
            'views': [(view_id, 'kanban'), (False, 'tree'), (False, 'form')],
            'domain': [('invoice_id', '=', ids[0])],
            'context': context,
            'target': 'current', # 'new'
            'nodestroy': False,
            }
        
    def generate_add_new_SSCC_code (self, cr, uid, ids, context=None):
        '''
        '''
        line_pool = self.pool.get('sscc.invoice.line')
        code_pool= self.pool.get('sscc.code')
        invoice_proxy = self.browse(cr, uid, ids, context=context)[0]
        codes = len(invoice_proxy.code_ids)
        code_id = code_pool.create(cr,uid, {
            'invoice_id': ids[0],
            }, context=context)
        if codes: 
            return True
        for line in invoice_proxy.line_ids:
            line_pool.write(cr, uid, line.id, {
                'sscc_id': code_id,
                }, context=context)
        return True

    # -------------------------------------------------------------------------
    # Export function:
    # -------------------------------------------------------------------------
    def export_invoice_csv(self, cr, uid, ids, context=None):
        ''' Import csv file
        '''

        # Initial setup_
        filename = '/home/thebrush/etl/MCS/export.csv' # TODO parametrize
        
        invoice_proxy = self.browse(cr, uid, ids, context=context)[0]
       
        f_out = open(filename, 'w')
       
        mask = '%-6s%-10s%-6s%-10s%-16s%-72s%-2s%-2s%-10s%-8s%-18s%-10s%-12s%-9s%-5s%-13s%-14s%-5s%-5s%-2s%-2s%-2s%-5s%-10s%-10s%-10s%-10s'
        
        for line in invoice_proxy.line_ids:
            f_out.write( mask % (
                invoice_proxy.name,
                invoice_proxy.date,
                line.order_number,
                line.order_date,
                line.code, 
                line.name, 
                line.uom, 
                line.currency,         
                line.price, 
                line.duty_code, 
                line.sscc_id.name,
                line.trade_number,
                line.quantity,
                line.q_x_pack,
                line.parcel,
                line.net_weight,
                line.weight,
                line.lot,
                line.deadline,
                line.country_origin,
                line.country_from,
                line.duty_ok,
                line.mnr_number,
                line.sanitary,
                line.sanitary_date,
                line.extra_code,
                line.sif,      
                ))
              
        return True
        
    # -------------------------------------------------------------------------
    # Import function:
    # -------------------------------------------------------------------------
    def import_invoice_csv(self, cr, uid, ids, context=None):
        ''' Import csv file
        '''
        # Pool used:
        line_pool = self.pool.get('sscc.invoice.line')
        partner_pool = self.pool.get('res.partner')

        # Initial setup_
        filename = '/home/thebrush/etl/MCS/fattura.csv' # TODO parametrize
        
        header = True
        invoice_id = False
        _logger.info('Import invoice %s' % filename)
        for line in open(filename, 'r'):
            # -----------------------------------------------------------------     
            # Header data:            
            # -----------------------------------------------------------------     
            if header:               
                header = False                

                # Fields:
                number_invoice = line[0:6] # 6
                date_invoice = line[6:16] # 10
                partner_code = line[284:293].strip() # 9 (end file)
                
                # Calculated fields:
                partner_id = False
                if partner_code: 
                    partner_ids = partner_pool.search(cr, uid, [
                        ('sql_customer_code', '=', partner_code),
                        ], context=context)
                    if partner_ids:
                        partner_id = partner_ids[0]
               
                # TODO check number invoice first
                
                # Create invoice header
                invoice_id = self.create(cr, uid, {
                    'name': number_invoice,
                    'date': date_invoice,
                    'year': date_invoice[:4],                    
                    'partner_id': partner_id,
                    'partner_code': partner_code,
                    #'journal':
                    }, context=context)
                        
            # -----------------------------------------------------------------     
            # Row data:
            # -----------------------------------------------------------------     
            # Fields:
            order_number = line[16:22] # 6
            order_date = line[22:32] # 10
            code = line[32:48] # 16
            description = line[48:120] # 72
            uom = line[120:122] # 2
            currency = line[122:124] # 2         
            price = line[124:134] # 10
            duty_code = line[134:142] # 8
            #sscc = line[142:160] # 18
            trade_number = line[160:170] # 10
            quantity = line[170:182] # 12
            q_x_pack = line[182:191] # 9
            parcel = line[191:196] # 5
            net_weight = line[196:209] # 13
            weight = line[209:223] # 14
            lot = line[223:228] # 5
            deadline = line[228:233] # 5
            country_origin = line[233:235] # 2
            country_from = line[235:237] # 2
            #duty_ok = line[237:239] # 2
            #mnr_number = line[239:244] # 5 
            #sanitary = line[244:254] # 10
            #sanitary_date = line[254:264] # 10
            #extra_code = line[264:274] # 10
            #sif = line[274:284] # 10            
            
            # Create invoice line 
            line_pool.create(cr, uid, {
                'invoice_id': invoice_id,
                'name': description,
                'code': code,
                'uom': uom,
                'currency': currency,
                'price': price, 
                'quantity': quantity,
                'order_date': order_date,
                'order_number': order_number,
                'duty_code': duty_code,
                'q_x_pack': q_x_pack,
                'quantity': quantity,
                'parcel': parcel,
                'net_weight': net_weight,
                'weight': weight,
                'lot': lot,
                'deadline': deadline,
                'country_origin': country_origin,
                'country_from': country_from,                 
                #'duty_ok'
                #'mnr_number'
                #'sanitary'
                #'sanitary_date'
                #'extra_code'
                #'sif' 
                }, context=context)
               
        return True # TODO return view with invoice!
        
    _columns = {
        'name': fields.char('Number', size=15, required=True),
        'date': fields.date('Date'),
        'year': fields.char('Year', size=4),
        'journal': fields.char('Journal', size=64), 
        'partner_code': fields.char('Partner code', size=9),
        'partner_id': fields.many2one('res.partner', 'Partner'),    
        'code_ids': fields.one2many(
            'sscc.code', 'invoice_id', 'Sscc Code'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('assigned', 'Assigned'),
            ('closed', 'Closed'),
            ], 'State', readonly=True),
        }
                 
        # Function complete code
        # TODO 1st char??    
    _defaults = {
        'state': lambda *x: 'draft',
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
        'price': fields.char('Price', size=12), 
        'currency': fields.char('currency', size=12), 
        'invoice_id': fields.many2one('sscc.invoice', 'Invoice'), 
        'sscc_id': fields.many2one('sscc.code', 'SSCC code'),
        'order_date': fields.date('Order date'),
        'order_number': fields.char('Order number', size=15), 
        'duty_code': fields.char('Duty code', size=8),
        #'sscc': fields.char('SSCC', size=18),
        'trade_number': fields.char('Trade number', size=10),
        'quantity': fields.char('Quantity', size=12),
        'q_x_pack': fields.char('Q_x_pack', size=9),
        'parcel': fields.char('Parcel', size=5),
        'net_weight': fields.char('Net_weight', size=13),
        'weight': fields.char('Weight', size=14),
        'lot': fields.char('Lot', size=10), #TODO
        'deadline': fields.char('Deadline', size=10),#TODO
        'country_origin': fields.char('Country origin', size=10),#TODO
        'country_from': fields.char('Country from', size=10), #TODO
        'duty_ok': fields.boolean('Duty ok?'),
        'mnr_number': fields.char('Mnr Number', size=10), #TODO
        'sanitary': fields.char('Sanitary', size=10), #TODO
        'sanitary_date': fields.char('Sanitary date', size=10), #TODO
        'extra_code': fields.char('Extra code', size=10), #TODO
        'sif': fields.char('Sif', size=10), #TODO 
        }
        
class SsccInvoice  (orm.Model):
    """ Model name: SsccInvoice
    """
    
    _inherit = 'sscc.invoice'
    
    _columns = {
        'line_ids': fields.one2many('sscc.invoice.line', 'invoice_id', 'Line'), 
        }
        
class SsccCode  (orm.Model):
    """ Model name: SsccCode
    """
    
    _inherit = 'sscc.code'
    
    _columns = {
        'line_ids': fields.one2many('sscc.invoice.line', 'sscc_id', 'Line'),        
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
