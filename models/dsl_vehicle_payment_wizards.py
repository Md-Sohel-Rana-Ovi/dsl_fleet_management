from odoo import models, fields, api
from datetime import datetime


class CreatePaymentMaintenanceRequest(models.TransientModel):
    _name = 'dsl.fleet.payment.request.wizard'


    # partner_id = fields.Many2one('res.partner', required=True, string='Request Person', default=lambda self: self.env.user)
    account_move_id = fields.Many2one(comodel_name="account.move")
    account_payment_id = fields.Many2one(comodel_name="account.payment")  
    # refuel_id = fields.Many2one('dsl.vehicle.refueling', 'Refuel', required=True)
    user_id = fields.Many2one(comodel_name='res.users', string='Request For Payment')
    partner_id = fields.Many2one(comodel_name="res.partner",string="Request Person")
    # name = fields.Char(related="student_id.name")
    journal_id = fields.Many2one(comodel_name='account.journal',
                                 string='Journal',
                                 required=True,
                                 domain="[('type', 'in', ('bank', 'cash'))]",
                                 default=lambda self: self.env['account.journal'].search([('type', '=', 'cash')]))

    company_id = fields.Many2one(comodel_name='res.company', default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    amount_residual = fields.Monetary(related="account_move_id.amount_residual")
    amount = fields.Monetary(string="Amount")
    is_payment_done = fields.Boolean(string="Is Payment Done?", default=False, readonly=True)
    total_payable_amount = fields.Monetary(related="user_id.partner_id.total_invoiced",
                                           string="Total Payable Amount")

   

    @api.depends('refuel_id')
    def _compute_user_id(self):
        for record in self:
            record.user_id = record.refuel_id.user_id
    

    def create_payment_maintenance(self):
        payment_vals = {
            'partner_id': self.user_id.partner_id.id,
            'journal_id': self.journal_id.id,
            'payment_type': 'outbound',
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'date': fields.Datetime.now(),
            'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id,
            'partner_type': 'supplier',
            'partner_bank_id': self.user_id.partner_id.bank_ids and self.user_id.partner_id.bank_ids[0].id or False,
            'ref': 'Vendor Payment',
        }

        payment = self.env['account.payment'].create(payment_vals)

        if self.account_move_id:
            invoice_ids = self.account_move_id.filtered(lambda move: move.is_invoice()).mapped('invoice_line_ids.invoice_id')
            payment.invoice_ids = invoice_ids

            # Create payment allocation for each invoice
            for invoice in invoice_ids:
                allocation_vals = {
                    'invoice_id': invoice.id,
                    'payment_id': payment.id,
                    'amount': self.amount,
                }
                allocation = self.env['account.payment.allocate'].create(allocation_vals)
                allocation._onchange_invoice_id()
                allocation.recompute_payment_allocation()

        self.account_payment_id = payment.id
        self.is_payment_done = True

        if payment.state == 'draft':
            payment.action_post()
        
        return True
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Vendor Payment',
        #     'res_model': 'account.payment',
        #     'res_id': payment.id,
        #     'view_mode': 'form',
        # }














    # def create_payment_maintenance(self):
    #     for rec in self:
    #         payment_vals = {
    #             'partner_id': self.partner_id.id,
    #             'journal_id': self.journal_id.id,
    #             'payment_type': 'outbound',
    #             'amount': self.amount,
    #             'currency_id': self.currency_id.id,
    #             'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    #             'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id,
    #             'partner_type': 'supplier',
    #             'partner_bank_id': self.partner_id.bank_ids and self.partner_id.bank_ids[0].id or False,
    #             'ref': 'Vendor Payment',  
    #         }

    #         payment = self.env['account.payment'].create(payment_vals)
    #         self.account_payment_id = payment.id
    #         self.is_payment_done = True

    #         if rec.account_payment_id.state == 'draft':
    #             rec.account_payment_id.action_post()

    #         return {
    #             'type': 'ir.actions.act_window',
    #             'name': 'Vendor Payment',
    #             'res_model': 'account.payment',
    #             'res_id': payment.id,
    #             'view_mode': 'form',
    #         }


    # def create_payment_maintenance(self):
    #     for rec in self:
    #         payment = self.env['account.payment']
    #         search_customer = payment.search([(
    #             'partner_id', '=', self.partner_id.id
    #         )])

    #         if not rec.account_payment_id:
    #             make_payment = search_customer.sudo().create({
    #                 "payment_type": "inbound",
    #                 "partner_id": rec.partner_id.id,
    #                 "journal_id": rec.journal_id.id,
    #                 "amount": rec.amount,
    #                 "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    #             })

    #             if make_payment:
    #                 rec.sudo().write({
    #                     "account_payment_id": make_payment.id,
    #                     "is_payment_done": True,
    #                 })

                # if rec.account_payment_id.state == 'draft':
                #     rec.account_payment_id.action_post()
    #                 # payment.state = 'posted'
    #             return True




    