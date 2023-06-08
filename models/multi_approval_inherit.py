from odoo import api, models, fields, _
from datetime import datetime, date
import logging

_logger = logging.getLogger(__name__)


class MultiApprovalTypeInherit(models.Model):
    _inherit = 'multi.approval.type'

    maintenance_type_id = fields.Many2one('dsl.maintenance.type', string='Type')


class MultiApproval(models.Model):
    _inherit = 'multi.approval'

    def action_approve(self):
        recs = self.filtered(lambda x: x.state == 'Submitted')
        for rec in recs:
            if not rec.is_pic:
                msg = _('{} do not have the authority to approve this request!'.format(rec.env.user.name))
                self.sudo().message_post(body=msg)
                return False
            line = rec.line_id
            if not line or line.state != 'Waiting for Approval':
                # Something goes wrong!
                self.message_post(body=_('Something goes wrong!'))
                return False

            # Update follower
            rec.update_follower(self.env.uid)

            # check if this line is required
            other_lines = rec.line_ids.filtered(
                lambda x: x.sequence >= line.sequence and x.state == 'Draft')
            if not other_lines:
                rec.state = 'Approved'
                msg = _('I Approved')
            else:
                next_line = other_lines.sorted('sequence')[0]
                next_line.write({
                    'state': 'Waiting for Approval',
                })
                rec.line_id = next_line
                msg = _('I Recommended')
            line.state = 'Approved'
            # msg = _('I Approved')
            rec.message_post(body=msg)

            model = self.env['ir.model'].sudo().search([('model', '=', 'dsl.maintenance.request')], order='id desc', limit=1)
            if model:
                if rec.type_id.model_id.id == model.id:
                    if rec.state == 'Approved':
                        booking = self.env['dsl.maintenance.request'].sudo().search([('approve_id', '=', rec.id)], order='id desc', limit=1)
                        if booking.state == 'submit':
                            booking.state = 'approve'

            model = self.env['ir.model'].sudo().search([('model', '=', 'dsl.vehicle.refueling')], order='id desc', limit=1)
            if model:
                if rec.type_id.model_id.id == model.id:
                    if rec.state == 'Approved':
                        booking = self.env['dsl.vehicle.refueling'].sudo().search([('approve_id', '=', rec.id)], order='id desc', limit=1)
                        if booking.state == 'submit':
                            booking.state = 'approve'                