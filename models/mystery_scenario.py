from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MysteryScenario(models.Model):
    _name = 'mystery.scenario'
    _description = 'Mystery Scenario'
    _order = 'name'

    name = fields.Char(required=True)
    description = fields.Text()
    difficulty = fields.Selection([
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ], default='medium', required=True)
    estimated_duration = fields.Integer(string='Estimated Duration (Minutes)', default=60, required=True)
    puzzle_ids = fields.Many2many(
        'mystery.puzzle',
        'mystery_scenario_puzzle_rel',
        'scenario_id',
        'puzzle_id',
        string='Puzzles',
    )
    puzzle_count = fields.Integer(compute='_compute_puzzle_count')
    active = fields.Boolean(default=True)

    _duration_positive = models.Constraint(
        'CHECK(estimated_duration > 0)',
        'Estimated duration must be greater than zero.',
    )

    @api.depends('puzzle_ids')
    def _compute_puzzle_count(self):
        for scenario in self:
            scenario.puzzle_count = len(scenario.puzzle_ids)
