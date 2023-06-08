# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class FleetVehicleRefueling(models.Model):
    _name = 'dsl.vehicle.refueling'  
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'service_type_id'
    _description = 'Refueling Request for vehicles'

    active = fields.Boolean(default=True)
    user_id = fields.Many2one('res.users', string='Request For')
    code = fields.Char(string='Code', required=True, copy=False,
                       readonly=True, index=True, default=lambda self: ('New'))
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', required=True)
    manager_id = fields.Many2one('res.users', 'Fleet Manager', related='vehicle_id.manager_id', store=True)
    amount = fields.Monetary('Cost')
    description = fields.Char('Description')
    driver_id = fields.Many2one('res.partner',related='vehicle_id.driver_id', string='Driver')
    odometer_id = fields.Many2one('fleet.vehicle.odometer', 'Odometer', help='Odometer measure of the vehicle at the moment of this log')
    odometer = fields.Float(
        compute="_get_odometer", inverse='_set_odometer', string='Odometer Value',
        help='Odometer measure of the vehicle at the moment of this log')
    odometer_unit = fields.Selection(related='vehicle_id.odometer_unit', string="Unit", readonly=True)
    date = fields.Date(help='Date when the cost has been executed', default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    purchaser_id = fields.Many2one('res.partner', string="Driver", compute='_compute_purchaser_id', readonly=False, store=True)
    inv_ref = fields.Char('Vendor Reference')
    vendor_id = fields.Many2one('res.partner', 'Vendor')
    notes = fields.Text()
    service_type_id = fields.Many2one(
        'fleet.service.type', 'Service Type', required=True,
        default=lambda self: self.env.ref('fleet.type_service_service_7', raise_if_not_found=False),
    )
    fuel_type = fields.Selection([
        ('diesel', 'Diesel'),
        ('gasoline', 'Gasoline'),
        ('full_hybrid', 'Full Hybrid'),
        ('plug_in_hybrid_diesel', 'Plug-in Hybrid Diesel'),
        ('plug_in_hybrid_gasoline', 'Plug-in Hybrid Gasoline'),
        ('cng', 'CNG'),
        ('lpg', 'LPG'),
        ('hydrogen', 'Hydrogen'),
        ('electric', 'Electric'),
    ], string='Fuel Type')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('approve', 'Approve'),
        ('payment', 'Payment'),
        ('bill', 'Generate Bill'),
        ('cancel', 'Cancelled'), ],
        string='Status', readonly=True, default='draft')
    is_approved = fields.Boolean(
        string='Is Approved', readonly="1", default=False, compute='_compute_approval_user')
    registration_date = fields.Datetime(string='Registration Date')
    approve_id = fields.Many2one('multi.approval', string="Approve By")
    approve_line_ids = fields.One2many(
        related='approve_id.line_ids', string="Approve Line")
    bill_count = fields.Integer(string="Invoice Count", compute='_get_bill_count')
    product_id = fields.Many2one('product.product', string='Product', default=lambda self: self._default_product_id())
    move_id = fields.Many2one('account.move', string='Invoice', readonly=True)
    def _default_product_id(self):
        return 0
    
    def _compute_approval_user(self):
        for rec in self:
            is_approved = False
            if rec.approve_id.state == 'Submitted':
                for line in rec.approve_id.line_ids:
                    if line.state != 'approve' and line.user_id.id == rec.env.uid:
                        is_approved = True
                        break
                    else:
                        self.is_approved = False
            rec.is_approved = is_approved
    

    
    # def payment_maintenance_request_view(self):
    #     return {
    #         'name': "Maintenance Payment",
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'dsl.fleet.payment.request.wizard',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'context': {
    #             'driver_id': self.id,
    #         },
    #     }

    def action_draft(self):
        self.state = 'draft'

    def action_payment(self):
        self.state = 'payment'
        return {
            'name': "Maintenance Payment",
            'type': 'ir.actions.act_window',
            'res_model': 'dsl.fleet.payment.request.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'driver_id': self.id,
            },
        }

    def action_approve(self):
        for rec in self:
            rec.approve_id.action_approve()
            if rec.approve_id.state == 'Approved':
                rec.state = 'approve'
                rec.registration_date = datetime.now()
                # self.create_invoice()

    def action_submit(self):
        for rec in self:
            model = self.env['ir.model'].sudo().search(
                [('model', '=', 'dsl.vehicle.refueling')], order='id desc', limit=1)
            approval_type_id = self.env['multi.approval.type'].search([('model_id', '=', model.id), ], order="id desc", limit=1)
            # ('maintenance_type_id', '=', rec.maintenance_type_id.id)
            if approval_type_id:
                approval = self.env['multi.approval'].sudo().create({
                    'name': 'Approval of ' + str(rec.code),
                    'type_id': approval_type_id.id,
                    'user_id': rec.manager_id.id,
                })
                if approval:
                    approval.action_submit()
                    rec.state = 'submit'
                    rec.approve_id = approval.id

    def action_request(self):
        self.state = 'request'


    def generate_bill(self):
        self.state = 'bill'
        invoice_vals = {
            'move_type': 'in_invoice',
            'partner_id': self.user_id.partner_id.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'quantity': 1,
                'price_unit': self.amount,
            })],
        }
        vendor_bill = self.env['account.move'].create(invoice_vals)
        # if vendor_bill.state == 'draft':
            # vendor_bill.action_post()
        self.move_id = vendor_bill.id
   
    def action_reset_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_cancel(self):
        self.state = 'cancel'

    def _get_bill_count(self):
        for rec in self:
            invoice_ids = self.env['account.move'].search([
                ('partner_id', '=', rec.user_id.partner_id.id),
                ('move_type', '=', 'in_invoice'),
                ('state', '=', 'draft')
            ])
            rec.bill_count = len(invoice_ids)     
              
   
    def action_view_bill(self):
        invoices = self.env['account.move'].search([('partner_id', '=', self.user_id.partner_id.id), ('move_type', '=', 'in_invoice'), ('state', '=', 'draft')])
        if invoices:
            action = {
                'name': 'Request Bill',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'views': [(False, 'tree'), (False, 'form')],
                'domain': [('id', 'in', invoices.ids)],
                'context': {'create': False}
            }
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code(
            'dsl.vehicle.refueling')
        result = super(FleetVehicleRefueling, self).create(vals)
        return result
