from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MysteryRoom(models.Model):
    _name = 'mystery.room'
    _description = 'Mystery Room'
    _order = 'name'

    name = fields.Char(string='Room Name', required=True)
    code = fields.Char(string='Room Code', required=True, copy=False)
    capacity = fields.Integer(string='Capacity', default=4, required=True)
    difficulty = fields.Selection([
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ], string='Difficulty', default='medium', required=True)
    duration_minutes = fields.Integer(string='Duration (Minutes)', default=60, required=True)
    price = fields.Float(string='Price', default=0.0)
    active = fields.Boolean(default=True)
    description = fields.Text()

    _code_unique = models.Constraint('UNIQUE(code)', 'Room code must be unique.')
    _capacity_positive = models.Constraint('CHECK(capacity > 0)', 'Room capacity must be greater than zero.')
    _duration_positive = models.Constraint('CHECK(duration_minutes > 0)', 'Room duration must be greater than zero.')
    _price_nonnegative = models.Constraint('CHECK(price >= 0)', 'Room price cannot be negative.')

    booking_ids = fields.One2many('mystery.booking', 'room_id', string='Bookings')
    booking_count = fields.Integer(compute='_compute_booking_count')

    @api.depends('booking_ids')
    def _compute_booking_count(self):
        for room in self:
            room.booking_count = len(room.booking_ids)
