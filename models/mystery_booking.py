from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MysteryBooking(models.Model):
    _name = 'mystery.booking'
    _description = 'Mystery Room Booking'
    _order = 'start_datetime desc, id desc'

    name = fields.Char(string='Booking Reference', required=True, copy=False, default='New')
    team_id = fields.Many2one('mystery.team', string='Team', required=True, ondelete='restrict')
    room_id = fields.Many2one('mystery.room', string='Room', required=True, ondelete='restrict')
    scenario_id = fields.Many2one('mystery.scenario', string='Scenario', required=True, ondelete='restrict')
    start_datetime = fields.Datetime(required=True)
    end_datetime = fields.Datetime(required=True)
    player_count = fields.Integer(string='Number of Players', default=4, required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='draft', required=True, copy=False)
    notes = fields.Text()
    session_ids = fields.One2many('mystery.session', 'booking_id', string='Game Sessions')

    _date_order = models.Constraint(
        'CHECK(end_datetime > start_datetime)',
        'The booking end time must be later than the start time.',
    )
    _players_positive = models.Constraint('CHECK(player_count > 0)', 'Player count must be greater than zero.')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('mystery.booking') or 'New'
        return super().create(vals_list)

    @api.constrains('player_count', 'room_id')
    def _check_player_capacity(self):
        for booking in self:
            if booking.room_id and booking.player_count > booking.room_id.capacity:
                raise ValidationError('The number of players cannot exceed the room capacity.')

    @api.constrains('start_datetime', 'end_datetime', 'room_id', 'state')
    def _check_room_overlap(self):
        for booking in self:
            if not booking.room_id or not booking.start_datetime or not booking.end_datetime:
                continue
            if booking.state not in ('confirmed', 'completed'):
                continue
            overlap = self.search_count([
                ('id', '!=', booking.id),
                ('room_id', '=', booking.room_id.id),
                ('state', 'in', ['confirmed', 'completed']),
                ('start_datetime', '<', booking.end_datetime),
                ('end_datetime', '>', booking.start_datetime),
            ])
            if overlap:
                raise ValidationError('This room already has a confirmed or completed booking during that time.')

    def action_confirm_booking(self):
        for booking in self:
            if booking.state != 'draft':
                raise ValidationError('Only draft bookings can be confirmed.')
            booking.state = 'confirmed'
        return True

    def action_complete_booking(self):
        for booking in self:
            if booking.state != 'confirmed':
                raise ValidationError('Only confirmed bookings can be completed.')
            booking.state = 'completed'
        return True

    def action_cancel_booking(self):
        for booking in self:
            if booking.state not in ('draft', 'confirmed'):
                raise ValidationError('Only draft or confirmed bookings can be cancelled.')
            booking.state = 'cancelled'
        return True

    def action_reset_to_draft(self):
        for booking in self:
            if booking.state == 'completed':
                raise ValidationError('Completed bookings cannot be reset to draft.')
            booking.state = 'draft'
        return True
