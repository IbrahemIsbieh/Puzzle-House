from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestMysteryBooking(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.room = cls.env['mystery.room'].create({
            'name': 'Test Mystery Room',
            'code': 'TEST-ROOM-001',
            'capacity': 6,
            'difficulty': 'medium',
            'duration_minutes': 60,
            'price': 25.0,
        })

        cls.team = cls.env['mystery.team'].create({
            'name': 'Test Team',
            'contact_name': 'Test Contact',
            'member_count': 4,
        })

        cls.scenario = cls.env['mystery.scenario'].create({
            'name': 'Test Scenario',
            'difficulty': 'medium',
            'estimated_duration': 60,
        })

        cls.start = fields.Datetime.to_datetime(
            '2026-11-10 10:00:00'
        )
        cls.end = fields.Datetime.to_datetime(
            '2026-11-10 11:00:00'
        )

    def _booking_values(self, **overrides):
        values = {
            'name': 'Test Booking',
            'team_id': self.team.id,
            'room_id': self.room.id,
            'scenario_id': self.scenario.id,
            'start_datetime': self.start,
            'end_datetime': self.end,
            'player_count': 4,
            'state': 'draft',
        }
        values.update(overrides)
        return values

    def test_create_booking(self):
        """A valid draft booking should be created successfully."""
        booking = self.env['mystery.booking'].create(
            self._booking_values()
        )

        self.assertTrue(booking.id)
        self.assertEqual(booking.state, 'draft')
        self.assertEqual(booking.player_count, 4)

    def test_overlapping_confirmed_booking(self):
        """Two confirmed bookings cannot overlap in the same room."""
        self.env['mystery.booking'].create(
            self._booking_values(
                name='First Booking',
                state='confirmed',
            )
        )

        with self.assertRaises(ValidationError):
            with self.cr.savepoint():
                self.env['mystery.booking'].create(
                    self._booking_values(
                        name='Overlapping Booking',
                        state='confirmed',
                        start_datetime=fields.Datetime.to_datetime(
                            '2026-11-10 10:30:00'
                        ),
                        end_datetime=fields.Datetime.to_datetime(
                            '2026-11-10 11:30:00'
                        ),
                    )
                )

    def test_cancelled_booking_does_not_block_room(self):
        """A cancelled booking should not reserve the room."""
        self.env['mystery.booking'].create(
            self._booking_values(
                name='Cancelled Booking',
                state='cancelled',
            )
        )

        booking = self.env['mystery.booking'].create(
            self._booking_values(
                name='Replacement Booking',
                state='confirmed',
            )
        )

        self.assertEqual(booking.state, 'confirmed')

    def test_confirm_booking_button(self):
        """The confirmation button should change draft to confirmed."""
        booking = self.env['mystery.booking'].create(
            self._booking_values()
        )

        booking.action_confirm_booking()

        self.assertEqual(booking.state, 'confirmed')
