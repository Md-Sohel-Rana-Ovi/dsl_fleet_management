from odoo import models, fields, api


class DslAccidentalCase(models.Model):
    _name = "dsl.accidental.case"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'vehicle_id'
    _description = "Dsl Accidental Case"


    code = fields.Char(string='Code', required=True, copy=False,
                       readonly=True, index=True, default=lambda self: ('New'))
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', required=True)
    manager_id = fields.Many2one('res.users', 'Fleet Manager', related='vehicle_id.manager_id', store=True)
    driver_id = fields.Many2one('res.partner',related='vehicle_id.driver_id', string='Driver')
    date = fields.Date(help='Date when the accident has been executed', default=fields.Date.context_today)
    active = fields.Boolean(string="Active", default=True, track_visibility='onchange')
    note = fields.Text(string='Note', track_visibility='onchange')

   

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code(
            'dsl.accidental.case')
        result = super(DslAccidentalCase, self).create(vals)
        return result
