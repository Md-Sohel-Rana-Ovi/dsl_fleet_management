from odoo import Command, models, fields
from datetime import datetime

class FleetVehicleExtension(models.Model):
    _inherit = 'fleet.vehicle'

    fueling_request_count = fields.Integer(string="Fuel Request Count", compute='_get_record_count')
    allocate_person = fields.Many2one('res.users', string='Allocate Person')
  
    def _get_record_count(self):
        for rec in self:
            record_ids = self.env['dsl.vehicle.refueling'].search([
                ('driver_id', '=', self.driver_id.id)
            ])
            rec.fueling_request_count = len(record_ids)  

    # def action_fueling_view(self):
    #     self.ensure_one()
    #     xml_id = self.env.context.get('xml_id')
    #     if xml_id:
    #         res = {
    #             'type': 'ir.actions.act_window',
    #             'name': 'Fueling Request',
    #             'view_mode': 'tree,form',
    #             'res_model': 'dsl.maintenance.request',  # Replace with the actual model name
    #             'target': 'current',
    #             'domain': [('vehicle_id', '=', self.id)],
    #             'context': dict(self.env.context, default_vehicle_id=self.id, group_by=False),
    #         }
    #         return res
    #     return False
    def action_fueling_view(self):
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:
            res = self.env['ir.actions.act_window']._for_xml_id('dsl_fleet_management.%s' % xml_id)
            res.update(
                context=dict(self.env.context, default_vehicle_id=self.id, group_by=False),
                domain=[('driver_id', '=', self.driver_id.id)]
            )
            return res
        else:
            action = {'type': 'ir.actions.act_window_close'}    
        return False




class FleetVehicleServiceExtension(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    
    code = fields.Char(string="Code", readonly=True, copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('fleet.vehicle.log.services.sequence'))
    user_id = fields.Many2one('res.users', string='Request For')
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
    active = fields.Boolean(string="Active", default=True,
                            track_visibility='onchange')
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