# -*- coding: utf-8 -*-
###############################################################################
#
# ODOO (ex OpenERP) 
# Open Source Management Solution
# Copyright (C) 2001-2015 Micronaet S.r.l. (<http://www.micronaet.it>)
# Developer: Nicola Riolini @thebrush (<https://it.linkedin.com/in/thebrush>)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################


import os
import sys
import logging
import openerp
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.tools.translate import _
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)


class AccountInvoiceImportSsccCsv(orm.TransientModel):
    ''' Wizard for import invoice
    '''
    _name = 'account.invoice.import.sscc.csv'

    # --------------------
    # Wizard button event:
    # --------------------
    def action_import(self, cr, uid, ids, context=None):
        ''' Event for button import
        '''
        if context is None: 
            context = {}        

        # view_sscc_invoice_tree
        # view_sscc_invoice_search
        model_pool = self.pool.get('ir.model.data')
        #view_id = model_pool.get_object_reference(
        #    cr, uid, 'module_name', 'view_name')[1]
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('SSCC invoice'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            #'res_id': 1,
            'res_model': 'sscc.invoice',
            #'view_id': view_id, # False
            'views': [(False, 'tree'), (False, 'form')],
            'domain': [('state', '=', 'draft')],
            'context': context,
            'target': 'current', # 'new'
            'nodestroy': False,
            }

    _columns = {
        'note': fields.text(
            'Import SSCC invoiceAnnotation',
            help='Procedure for import invoice'),
        }
        
    _defaults = {
        'note': lambda *x: '''
            <p>
                Import procedure for assign <b>SSCC</b> code, before launch the
                import button please export form account, with the correct
                procedure, the invoice document, after press the button here.
            <p>
            </p>                
                All the invoice are in draft mode for assigned correct 
                SSCC code and link the product, after export <b>XLS</b> file 
                and print label for pallet.
            </p>
            ''',
        }    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


