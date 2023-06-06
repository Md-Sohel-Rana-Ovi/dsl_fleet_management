from odoo import models, fields, api


class DslMaintenanceType(models.Model):
    _name = "dsl.maintenance.type"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Dsl Maintenance Type"

    name = fields.Char(string='Name', track_visibility='onchange')
    active = fields.Boolean(string="Active", default=True, track_visibility='onchange')
    note = fields.Text(string='Note', track_visibility='onchange')

