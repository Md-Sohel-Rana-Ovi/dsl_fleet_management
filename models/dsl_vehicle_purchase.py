 # -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class VehiclePurchase(models.Model):
    _name = 'dsl.vehicle.purchase'  
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'model_id'
    _description = 'Vehicle Purchase History'   
    
    code = fields.Char(string='Code', required=True, copy=False,
                       readonly=True, index=True, default=lambda self: ('New'))
    partner_id = fields.Many2one('res.partner', string='Vendor')
    serial_number = fields.Char(string = 'Serial Number')
    model_id = fields.Many2one('fleet.vehicle.model',string = 'Model')

    purchase_order_number = fields.Char(string = 'Purchase Order Number')
    challan_number = fields.Char(string = 'Challan Number')
    warranty_guarantee_selection = fields.Selection(
        string = 'Warranty/Guarantee',
        selection = [
            ('Warranty', 'Warranty'),
            ('Guarantee', 'Guarantee')
        ],
        default = ''
    )
    warranty_guarantee_date_selection = fields.Date(string = 'Warranty/Guarantee Date')
    expiry_date = fields.Date(string = 'Expiry Date')
    location = fields.Char(string = 'Location')
    date_of_issue = fields.Date(string = 'Issue Date', default = fields.Date.today())
    date_of_purchase_approve = fields.Date(string = 'Purchase Approve Date', default = fields.Date.today())
    active = fields.Boolean(string="Active", default=True, track_visibility='onchange')
    note = fields.Text(string='Note', track_visibility='onchange')


    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code(
            'dsl.vehicle.purchase')
        result = super(VehiclePurchase, self).create(vals)
        return result