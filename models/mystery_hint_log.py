from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MysteryHintLog(models.Model):
    _name = 'mystery.hint.log'
    _description = 'Mystery Hint Log'
    _order = 'used_datetime desc'

    session_id = fields.Many2one('mystery.session', string='Game Session', required=True, ondelete='cascade')
    puzzle_id = fields.Many2one('mystery.puzzle', string='Puzzle', ondelete='restrict')
    hint_text = fields.Text(string='Hint Used', required=True)
    used_datetime = fields.Datetime(string='Used At', default=fields.Datetime.now, required=True)
    penalty_points = fields.Integer(string='Penalty Points', default=0)

    @api.constrains('session_id', 'puzzle_id', 'penalty_points')
    def _check_hint_values(self):
        for log in self:
            if log.penalty_points < 0:
                raise ValidationError('Penalty points cannot be negative.')
            if log.session_id and log.session_id.state != 'running':
                raise ValidationError('Hints can only be recorded while the game is running.')
            if log.session_id and log.puzzle_id and log.puzzle_id not in log.session_id.puzzle_ids:
                raise ValidationError('This puzzle does not belong to the session scenario.')
