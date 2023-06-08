from odoo import models, fields, api
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class PaymentRequest(models.Model):
    _name = 'dsl.maintenance.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Maintenance Request'

    name = fields.Char(string='Name', track_visibility='onchange')
    code = fields.Char(string='Code', required=True, copy=False,
                       readonly=True, index=True, default=lambda self: ('New'))
    user_id = fields.Many2one('res.users', string='Request For')
    driver_id = fields.Many2one('res.partner', string='Driver')
    allocate_person = fields.Many2one('res.users', string='Allocate Person')
    move_id = fields.Many2one('account.move', string='Invoice', readonly=True)
    product_id = fields.Many2one('product.product', string='Product')
    date = fields.Date(string='Date')
    maintenance_type_id = fields.Many2one(
        'dsl.maintenance.type', string='Request Type')
    responsible_person = fields.Many2one(
        'res.users', string='Responsible Person')
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
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicles')
    amount = fields.Float(string='Amount')
    active = fields.Boolean(string="Active", default=True,
                            track_visibility='onchange')
    note = fields.Text(string='Note', track_visibility='onchange')
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
    application_date = fields.Datetime(
        string='Application Date', default=lambda self: fields.Datetime.now())
    registration_date = fields.Datetime(string='Registration Date')
    approve_id = fields.Many2one('multi.approval', string="Approve By")
    approve_line_ids = fields.One2many(
        related='approve_id.line_ids', string="Approve Line")
    bill_count = fields.Integer(string="Invoice Count", compute='_get_bill_count')
   
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
    

    # def _get_bill_count(self):
    #     for rec in self:
    #         invoice_ids = self.env['account.move'].search([('ref', '=', rec.id), ('user_id', '=', rec.user_id.partner_id.id)])

    #         rec.bill_count = len(invoice_ids)
       

    # def action_view_bill(self):
    #     return {
    #         'name': 'Request Bill',
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'tree,form',
    #         'res_model': 'account.move',
    #         'domain': [('ref', '=', self.id)],
    #         'context': {'create': False}
    #     }
    def payment_maintenance_request_view(self):
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
                [('model', '=', 'dsl.maintenance.request')], order='id desc', limit=1)
            approval_type_id = self.env['multi.approval.type'].search([('model_id', '=', model.id), (
                'maintenance_type_id', '=', rec.maintenance_type_id.id)], order="id desc", limit=1)
            if approval_type_id:
                approval = self.env['multi.approval'].sudo().create({
                    'name': 'Approval of ' + str(rec.code),
                    'type_id': approval_type_id.id,
                    'user_id': rec.user_id.id,
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
              
    # def action_view_bill(self):
    #     invoices = self.env['account.move'].search([('partner_id', '=', self.user_id.partner_id.id), ('move_type', '=', 'in_invoice'), ('state', '=', 'draft')])
    #     if invoices:
    #         action = {
    #             'name': 'Request Bill',
    #             'type': 'ir.actions.act_window',
    #             'view_mode': 'form',
    #             'res_model': 'account.move',
    #             'res_id': invoices.ids[0],
    #             'context': {'create': False},
    #         }
    #     else:
    #         action = {'type': 'ir.actions.act_window_close'}
    #     return action

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
            'dsl.maintenance.request')
        result = super(PaymentRequest, self).create(vals)
        return result

