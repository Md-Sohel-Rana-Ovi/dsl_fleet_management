# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
from num2words import num2words


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
    # odometer_id = fields.Many2one('fleet.vehicle.odometer', 'Odometer', help='Odometer measure of the vehicle at the moment of this log')
    # odometer = fields.Float(
    #     compute="_get_odometer", inverse='_set_odometer', string='Odometer Value',
    #     help='Odometer measure of the vehicle at the moment of this log')
    # odometer_unit = fields.Selection(related='vehicle_id.odometer_unit', string="Unit", readonly=True)
    date = fields.Date(help='Date when the cost has been executed', default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    purchaser_id = fields.Many2one('res.partner', string="Driver", compute='_compute_purchaser_id', readonly=False, store=True)
    inv_ref = fields.Char('Vendor Reference')
    vendor_id = fields.Many2one('res.partner', 'Vendor')
    purchase_po_id = fields.Many2one('uom.uom',string="Purchase UoM")
    fuel_qty = fields.Float(string='Fuel Qty')
    # fuel_unit = fields.Selection(string="Fuel Unit", readonly=True)
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
        string='Status', readonly=True, default='draft', group_expand='_expand_states')
    is_approved = fields.Boolean(
        string='Is Approved', readonly="1", default=False, compute='_compute_approval_user')
    registration_date = fields.Datetime(string='Registration Date')
    approve_id = fields.Many2one('multi.approval', string="Approve By")
    approve_line_ids = fields.One2many(related='approve_id.line_ids', string="Approve Line")
    bill_count = fields.Integer(string="Invoice Count", compute='_get_bill_count')
    total_invoice_count = fields.Integer(string="Invoice", compute='_get_total_bill_count')
    # product_id = fields.Many2one('product.product', string='Product', default=lambda self: self._default_product_id())
    product_id = fields.Many2one('product.product', string='Product', default=lambda self: self.env['product.product'].search([('name', '=', 'Fueling Charge')], limit=1).id)
    move_id = fields.Many2one('account.move', string='Invoice', readonly=True)
    payment_id = fields.Many2one('account.payment', string='Payment', readonly=True)
    
    
    # def generate_fueling_money_receip_report(self):
    #     return self.env.ref('account.action_report_payment_receipt').report_action(self)
    
    def generate_fueling_money_receip_report(self):
        user_partner_id = self.user_id.partner_id.id

        payment_model = self.env['account.payment']
        payment_record = payment_model.search([('partner_id', '=', user_partner_id)], limit=1)

        if payment_record:
            report = self.env.ref('account.action_report_payment_receipt')
            return report.report_action(payment_record)
        else:
   
            return None



    @api.onchange('fuel_qty')
    def _onchange_fuel_qty_product_id(self):
        for rec in self:
            if rec.fuel_qty:
                rec.amount = rec.fuel_qty * rec.product_id.list_price
            else:
                rec.amount = 0.0
       
        
    
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
    

    
    # def _get_odometer(self):
    #     self.odometer = 0
    #     for record in self:
    #         if record.odometer_id:
    #             record.odometer = record.odometer_id.value

    # def _set_odometer(self):
    #     for record in self:
    #         if not record.odometer:
    #             raise UserError(_('Emptying the odometer value of a vehicle is not allowed.'))
    #         odometer = self.env['fleet.vehicle.odometer'].create({
    #             'value': record.odometer,
    #             'date': record.date or fields.Date.context_today(record),
    #             'vehicle_id': record.vehicle_id.id
    #         })
    #         self.odometer_id = odometer

    def action_draft(self):
        self.state = 'draft'

    def action_payment(self):
        self.state = 'payment'
        return {
            'name': "Refueling Payment",
            'type': 'ir.actions.act_window',
            'res_model': 'dsl.fleet.payment.request.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'user_id': self.id,
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
                'price_unit': self.product_id.list_price,
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
              
    def _get_total_bill_count(self):
        for rec in self:
            invoice_ids = self.env['account.move'].search([
                ('partner_id', '=', rec.user_id.partner_id.id),
                ('move_type', '=', 'in_invoice'),
                ('state', '!=', 'draft')
            ])
            rec.total_invoice_count = len(invoice_ids)  

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

    def action_total_view_bill(self):
        invoices = self.env['account.move'].search([('partner_id', '=', self.user_id.partner_id.id), ('move_type', '=', 'in_invoice'), ('state', '!=', 'draft')])
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
     
    def _expand_states(self, states, domain, order):
        return [key for key, dummy in type(self).state.selection]

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code(
            'dsl.vehicle.refueling')
        result = super(FleetVehicleRefueling, self).create(vals)
        return result


class AccountInvoice(models.Model):
    _inherit = 'account.payment'

    amount_in_words = fields.Char(compute='amount_word', string='Amount', readonly=True)
    print_to_report = fields.Boolean("Show in Report", default=True)
    refueling_id = fields.Many2one('dsl.vehicle.refueling', string='Refueling')
    currency_id = fields.Many2one('res.currency', string='Currency')

    @api.depends('amount')
    def amount_word(self):
        self.ensure_one()

        language = 'en'

        list_lang = [['en', 'en_US'], ['en', 'en_AU'], ['en', 'en_GB'], ['en', 'en_IN'],
                     ['fr', 'fr_BE'], ['fr', 'fr_CA'], ['fr', 'fr_CH'], ['fr', 'fr_FR'],
                     ['es', 'es_ES'], ['es', 'es_AR'], ['es', 'es_BO'], ['es', 'es_CL'], ['es', 'es_CO'],
                     ['es', 'es_CR'], ['es', 'es_DO'],
                     ['es', 'es_EC'], ['es', 'es_GT'], ['es', 'es_MX'], ['es', 'es_PA'], ['es', 'es_PE'],
                     ['es', 'es_PY'], ['es', 'es_UY'], ['es', 'es_VE'],
                     ['lt', 'lt_LT'], ['lv', 'lv_LV'], ['no', 'nb_NO'], ['pl', 'pl_PL'], ['ru', 'ru_RU'],
                     ['dk', 'da_DK'], ['pt_BR', 'pt_BR'], ['de', 'de_DE'], ['de', 'de_CH'],
                     ['ar', 'ar_SY'], ['it', 'it_IT'], ['he', 'he_IL'], ['id', 'id_ID'], ['tr', 'tr_TR'],
                     ['nl', 'nl_NL'], ['nl', 'nl_BE'], ['uk', 'uk_UA'], ['sl', 'sl_SI'], ['th', 'th_TH']]

        cnt = 0
        for rec in list_lang[cnt:len(list_lang)]:
            if rec[1] == self.partner_id.lang:
                language = rec[0]
            cnt += 1

        if language == 'th':
            self.amount_in_words = bahttext(self.amount)
            return

        amount_str = str('{:.2f}'.format(self.amount))
        amount_str_splt = amount_str.split('.')
        before_point_value = amount_str_splt[0]
        after_point_value = amount_str_splt[1][:2]

        before_amount_words = num2words(int(before_point_value), lang=language)
        after_amount_words = num2words(int(after_point_value), lang=language)

        amount = before_amount_words

        if self.currency_id:
            if self.currency_id.currency_unit_label:
                amount = amount + ' ' + self.currency_id.currency_unit_label

            if hasattr(self.currency_id, 'amount_separator'):
                amount = amount + ' ' + self.currency_id.amount_separator

            amount = amount + ' ' + after_amount_words

            if self.currency_id.currency_subunit_label:
                amount = amount + ' ' + self.currency_id.currency_subunit_label

        self.amount_in_words = amount

