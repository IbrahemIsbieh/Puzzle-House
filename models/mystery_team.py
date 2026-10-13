from odoo import api, fields, models


class MysteryTeam(models.Model):
    _name = 'mystery.team'
    _description = 'Mystery Team'
    _order = 'name'

    name = fields.Char(
        string='Team Name',
        required=True,
    )

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contact',
        ondelete='restrict',
        index=True,
    )

    contact_name = fields.Char(
        string='Contact Name',
    )

    phone = fields.Char(
        string='Phone',
    )

    email = fields.Char(
        string='Email',
    )

    member_count = fields.Integer(
        string='Number of Members',
        default=4,
        required=True,
    )

    notes = fields.Text(
        string='Notes',
    )

    booking_ids = fields.One2many(
        comodel_name='mystery.booking',
        inverse_name='team_id',
        string='Bookings',
    )

    booking_count = fields.Integer(
        string='Booking Count',
        compute='_compute_booking_count',
    )

    active = fields.Boolean(
        default=True,
    )

    _members_positive = models.Constraint(
        'CHECK(member_count > 0)',
        'Team must have at least one member.',
    )

    @api.depends('booking_ids')
    def _compute_booking_count(self):
        for team in self:
            team.booking_count = len(team.booking_ids)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        for team in self:
            if team.partner_id:
                team.contact_name = team.partner_id.name
                team.phone = team.partner_id.phone or team.partner_id.mobile
                team.email = team.partner_id.email