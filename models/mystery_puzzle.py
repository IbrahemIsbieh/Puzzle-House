from odoo import fields, models


class MysteryPuzzle(models.Model):
    _name = 'mystery.puzzle'
    _description = 'Mystery Puzzle'
    _order = 'name'

    name = fields.Char(string='Puzzle Name', required=True)
    code = fields.Char(string='Puzzle Code', required=True, copy=False)
    difficulty = fields.Selection([
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ], default='medium', required=True)
    question = fields.Text(required=True)
    answer = fields.Char(required=True)
    hint = fields.Text()
    points = fields.Integer(default=10, required=True)
    active = fields.Boolean(default=True)
    scenario_ids = fields.Many2many(
        'mystery.scenario',
        'mystery_scenario_puzzle_rel',
        'puzzle_id',
        'scenario_id',
        string='Scenarios',
    )

    _code_unique = models.Constraint('UNIQUE(code)', 'Puzzle code must be unique.')
    _points_nonnegative = models.Constraint('CHECK(points >= 0)', 'Puzzle points cannot be negative.')
