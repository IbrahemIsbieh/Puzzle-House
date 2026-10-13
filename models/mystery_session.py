from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MysterySession(models.Model):
    _name = 'mystery.session'
    _description = 'Mystery Game Session'
    _order = 'start_datetime desc, id desc'

    name = fields.Char(string='Session Reference', required=True, copy=False, default='New')
    booking_id = fields.Many2one('mystery.booking', string='Booking', required=True, ondelete='restrict')
    team_id = fields.Many2one('mystery.team', related='booking_id.team_id', store=True, readonly=True)
    room_id = fields.Many2one('mystery.room', related='booking_id.room_id', store=True, readonly=True)
    scenario_id = fields.Many2one('mystery.scenario', related='booking_id.scenario_id', store=True, readonly=True)
    start_datetime = fields.Datetime(required=True)
    end_datetime = fields.Datetime()
    state = fields.Selection([
        ('planned', 'Planned'),
        ('running', 'Running'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('cancelled', 'Cancelled'),
    ], default='planned', required=True, copy=False)
    puzzle_ids = fields.Many2many('mystery.puzzle', string='Scenario Puzzles', related='scenario_id.puzzle_ids', readonly=True)
    attempt_ids = fields.One2many('mystery.puzzle.attempt', 'session_id', string='Puzzle Attempts')
    hint_log_ids = fields.One2many('mystery.hint.log', 'session_id', string='Hint History')
    attempt_count = fields.Integer(compute='_compute_statistics', store=True)
    correct_attempt_count = fields.Integer(compute='_compute_statistics', store=True)
    success_rate = fields.Float(compute='_compute_statistics', store=True, digits=(5, 2))
    hint_count = fields.Integer(compute='_compute_statistics', store=True)
    score = fields.Integer(compute='_compute_statistics', store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('mystery.session') or 'New'
        return super().create(vals_list)

    @api.constrains('start_datetime', 'end_datetime')
    def _check_date_order(self):
        for session in self:
            if session.end_datetime and session.start_datetime and session.end_datetime < session.start_datetime:
                raise ValidationError('The session end time cannot be earlier than the start time.')

    @api.depends(
        'attempt_ids',
        'attempt_ids.is_correct',
        'attempt_ids.points_awarded',
        'hint_log_ids',
        'hint_log_ids.penalty_points',
    )
    def _compute_statistics(self):
        for session in self:
            attempts = session.attempt_ids
            correct_count = sum(1 for attempt in attempts if attempt.is_correct)
            earned_points = sum(attempt.points_awarded for attempt in attempts)
            penalties = sum(log.penalty_points for log in session.hint_log_ids)
            session.attempt_count = len(attempts)
            session.correct_attempt_count = correct_count
            session.success_rate = (correct_count / len(attempts) * 100.0) if attempts else 0.0
            session.hint_count = len(session.hint_log_ids)
            session.score = max(0, earned_points - penalties)

    def action_start_game(self):
        for session in self:
            if session.state != 'planned':
                raise ValidationError('Only planned sessions can be started.')
            if session.booking_id.state != 'confirmed':
                raise ValidationError('The booking must be confirmed before starting the game.')
            session.state = 'running'
        return True

    def action_win_game(self):
        for session in self:
            if session.state != 'running':
                raise ValidationError('Only running sessions can be marked as won.')
            session.state = 'won'
            session.end_datetime = fields.Datetime.now()
        return True

    def action_lose_game(self):
        for session in self:
            if session.state != 'running':
                raise ValidationError('Only running sessions can be marked as lost.')
            session.state = 'lost'
            session.end_datetime = fields.Datetime.now()
        return True

    def action_cancel_game(self):
        for session in self:
            if session.state not in ('planned', 'running'):
                raise ValidationError('Only planned or running sessions can be cancelled.')
            session.state = 'cancelled'
            session.end_datetime = fields.Datetime.now()
        return True
