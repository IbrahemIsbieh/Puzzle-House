from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MysteryPuzzleAttempt(models.Model):
    _name = 'mystery.puzzle.attempt'
    _description = 'Mystery Puzzle Attempt'
    _order = 'attempt_datetime desc, id desc'

    session_id = fields.Many2one('mystery.session', string='Game Session', required=True, ondelete='cascade')
    puzzle_id = fields.Many2one('mystery.puzzle', string='Puzzle', required=True, ondelete='restrict')
    answer_submitted = fields.Char(string='Submitted Answer', required=True)
    is_correct = fields.Boolean(compute='_compute_result', store=True)
    attempt_datetime = fields.Datetime(default=fields.Datetime.now, required=True)
    points_awarded = fields.Integer(compute='_compute_result', store=True)
    notes = fields.Text()

    @api.depends('answer_submitted', 'puzzle_id', 'puzzle_id.answer', 'puzzle_id.points')
    def _compute_result(self):
        for attempt in self:
            submitted = (attempt.answer_submitted or '').strip().casefold()
            answer = (attempt.puzzle_id.answer or '').strip().casefold() if attempt.puzzle_id else ''
            correct = bool(submitted and answer and submitted == answer)
            attempt.is_correct = correct
            attempt.points_awarded = attempt.puzzle_id.points if correct and attempt.puzzle_id else 0

    @api.constrains('session_id', 'puzzle_id')
    def _check_puzzle_belongs_to_scenario(self):
        for attempt in self:
            if attempt.session_id and attempt.puzzle_id and attempt.puzzle_id not in attempt.session_id.puzzle_ids:
                raise ValidationError('This puzzle does not belong to the session scenario.')

    @api.constrains('session_id')
    def _check_session_is_running(self):
        for attempt in self:
            if attempt.session_id and attempt.session_id.state != 'running':
                raise ValidationError('Puzzle attempts can only be recorded while the game session is running.')
