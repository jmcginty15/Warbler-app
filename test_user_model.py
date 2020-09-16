"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

class UserModelTestCase(TestCase):
    """Test models for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        # Use the signup class method to create users
        u1 = User.signup(
            email="test@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        u2 = User.signup(
            email='test2@test.com',
            username='testuser2',
            password='HASHED_PASSWORD_2'
        )

        db.session.commit()

        # Test authentication class method
        self.assertEqual(User.authenticate('testuser1', 'HASHED_PASSWORD'), u1)
        self.assertEqual(User.authenticate('testuser1', 'THE_WRONG_PASSWORD'), False)
        self.assertEqual(User.authenticate('thewrongusername', 'HASHED_PASSWORD'), False)

        # User should have no messages & no followers
        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)

        # Test __repr__ method
        self.assertEqual(u1.__repr__(), '<User #1: testuser1, test@test.com>')
        
        # Passwords should be hashed and therefore should not be stored as the entered password
        self.assertNotEqual(u1.password, 'HASHED_PASSWORD')
        self.assertNotEqual(u2.password, 'HASHED_PASSWORD_2')

        # Have u2 follow u1
        u1.followers.append(u2)
        db.session.commit()

        # Test follower methods
        self.assertEqual(u1.is_following(u2), False)
        self.assertEqual(u1.is_followed_by(u2), True)
        self.assertEqual(u2.is_following(u1), True)
        self.assertEqual(u2.is_followed_by(u1), False)
