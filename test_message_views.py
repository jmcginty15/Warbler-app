"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)

        db.session.commit()

    def test_add_delete_message(self):
        """Can user add and delete a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

            # Delete message
            res = c.post(f'/messages/{msg.id}/delete')

            self.assertEqual(res.status_code, 302)
            msg = Message.query.one_or_none()
            self.assertEqual(msg, None)

            # Mimic logging out
            with c.session_transaction() as sess:
                del sess[CURR_USER_KEY]
            
            # Make sure posting messages is not allowed when logged out
            res = c.post('/messages/new', data={'text': 'yeet'})
            self.assertEqual(res.status_code, 302)            
            res = c.post('/messages/new', data={'text': 'yeet'}, follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn('Access unauthorized.', html)

            # Add new message to test delete
            msg = Message(text='yeet', user_id=self.testuser.id)
            db.session.add(msg)
            db.session.commit()

            # Make sure deleting messages is not allowed when logged out
            res = c.post(f'/messages/{msg.id}/delete')
            self.assertEqual(res.status_code, 302)            
            res = c.post(f'/messages/{msg.id}/delete', follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn('Access unauthorized.', html)
    
    def test_delete(self):
        """Make sure a user cannot delete a message posted by a different user"""

        # Log in test user 2
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser2.id
            
            # Add new message to test delete
            msg = Message(text='yeet', user_id=1)
            db.session.add(msg)
            db.session.commit()
            
            # Make sure user 2 cannot delete a message posted by user 1
            res = c.post(f'/messages/{msg.id}/delete')
            self.assertEqual(res.status_code, 302)            
            res = c.post(f'/messages/{msg.id}/delete', follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn('Access unauthorized.', html)

