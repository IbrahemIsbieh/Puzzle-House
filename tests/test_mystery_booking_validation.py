from odoo import fields
from odoo.tests.common import TransactionCase
from psycopg2.errors import CheckViolation


class TestMysteryBookingValidation(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.room = cls.env['mystery.room'].create({
            'name': 'Validation Test Room',
            'code': 'VALIDATION-ROOM-001',
            'capacity': 4,
            'difficulty': 'easy',
            'duration_minutes': 60,
            'price': 20.0,
        })

        cls.team = cls.env['mystery.team'].create({
            'name': 'Validation Test Team',
            'contact_name': 'Test Contact',
            'member_count': 5,
        })

        cls.scenario = cls.env['mystery.scenario'].create({
            'name': 'Validation Test Scenario',
            'difficulty': 'easy',
            'estimated_duration': 60,
        })

    def _booking_values(self, **overrides):
        values = {
            'name': 'Validation Test Booking',
            'team_id': self.team.id,
            'room_id': self.room.id,
            'scenario_id': self.scenario.id,
            'start_datetime': fields.Datetime.to_datetime(
                '2026-11-20 10:00:00'
            ),
            'end_datetime': fields.Datetime.to_datetime(
                '2026-11-20 11:00:00'
            ),
            'player_count': 3,
            'state': 'draft',
        }

        values.update(overrides)
        return values

    def test_booking_player_count_exceeds_room_capacity(self):
        """A booking exceeding room capacity should be rejected."""

        with self.assertRaises(Exception):
            with self.cr.savepoint():
                self.env['mystery.booking'].create(
                    self._booking_values(
                        player_count=5,
                    )
                )

    def test_booking_end_before_start(self):
        """A booking ending before it starts should be rejected."""

        with self.assertRaises(CheckViolation):
            with self.cr.savepoint():
                self.env['mystery.booking'].create(
                    self._booking_values(
                        start_datetime=fields.Datetime.to_datetime(
                            '2026-11-20 12:00:00'
                        ),
                        end_datetime=fields.Datetime.to_datetime(
                            '2026-11-20 11:00:00'
                        ),
                    )
                )
