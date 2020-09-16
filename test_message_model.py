"""Message model tests."""

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

class MessageModelTestCase(TestCase):
    """Test models for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_message_model(self):
        """Does basic model work?"""

        # Create a test user
        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        # Create test messages
        m1 = Message(text='Test message 1', user_id=1)
        m2 = Message(text='Test message 2', user_id=1)
        db.session.add(m1)
        db.session.add(m2)
        db.session.commit()

        # Test relationship between messages and user
        self.assertEqual(m1.user, u)
        self.assertEqual(m2.user, u)
        self.assertIn(m1, u.messages)
        self.assertIn(m2, u.messages)
