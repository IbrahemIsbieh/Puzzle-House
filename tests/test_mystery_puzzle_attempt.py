from odoo.tests.common import TransactionCase


class TestMysteryPuzzleAttempt(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create room
        cls.room = cls.env['mystery.room'].create({
            'name': 'Puzzle Test Room',
            'code': 'TEST-ROOM-ATTEMPT',
            'capacity': 6,
            'difficulty': 'easy',
            'duration_minutes': 60,
            'price': 20.0,
        })

        # Create team
        cls.team = cls.env['mystery.team'].create({
            'name': 'Puzzle Test Team',
            'contact_name': 'Test Contact',
            'member_count': 3,
        })

        # Create puzzle
        cls.puzzle = cls.env['mystery.puzzle'].create({
            'name': 'Capital City',
            'code': 'TEST-PUZZLE-001',
            'difficulty': 'easy',
            'question': 'What is the capital of France?',
            'answer': 'Paris',
            'points': 10,
        })

        # Create scenario and link the puzzle to it
        cls.scenario = cls.env['mystery.scenario'].create({
            'name': 'Puzzle Test Scenario',
            'difficulty': 'easy',
            'estimated_duration': 60,
            'puzzle_ids': [(6, 0, [cls.puzzle.id])],
        })

        # Create booking
        cls.booking = cls.env['mystery.booking'].create({
            'name': 'Puzzle Test Booking',
            'team_id': cls.team.id,
            'room_id': cls.room.id,
            'scenario_id': cls.scenario.id,
            'start_datetime': '2026-11-20 10:00:00',
            'end_datetime': '2026-11-20 11:00:00',
            'player_count': 3,
        })

        # Create running session
        cls.session = cls.env['mystery.session'].create({
            'name': 'Puzzle Test Session',
            'booking_id': cls.booking.id,
            'start_datetime': '2026-11-20 10:00:00',
            'end_datetime': '2026-11-20 11:00:00',
            'state': 'running',
        })

    def _create_attempt(self, answer):
        return self.env['mystery.puzzle.attempt'].create({
            'session_id': self.session.id,
            'puzzle_id': self.puzzle.id,
            'answer_submitted': answer,
        })

    def test_correct_answer(self):
        attempt = self._create_attempt('Paris')

        self.assertTrue(attempt.is_correct)
        self.assertEqual(attempt.points_awarded, 10)

    def test_answer_is_case_insensitive(self):
        attempt = self._create_attempt('  pArIs  ')

        self.assertTrue(attempt.is_correct)
        self.assertEqual(attempt.points_awarded, 10)

    def test_wrong_answer(self):
        attempt = self._create_attempt('London')

        self.assertFalse(attempt.is_correct)
        self.assertEqual(attempt.points_awarded, 0)