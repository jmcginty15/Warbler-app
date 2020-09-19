"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


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


class UserViewTestCase(TestCase):
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
    
    def test_user_views_logged_out(self):
        """Make sure user cannot see follower/following/likes pages when logged out"""

        with self.client as c:

            # Followers page
            res = c.get('/users/1/followers')
            self.assertEqual(res.status_code, 302)
            res = c.get('/users/1/followers', follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn('Access unauthorized.', html)

            # Following page
            res = c.get('/users/1/following')
            self.assertEqual(res.status_code, 302)
            res = c.get('/users/1/following', follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn('Access unauthorized.', html)

            # Likes page
            res = c.get('/users/1/likes')
            self.assertEqual(res.status_code, 302)
            res = c.get('/users/1/likes', follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn('Access unauthorized.', html)
    
    def test_user_views_logged_in(self):
        """Test user views with a user logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Followers page
            res = c.get(f'/users/{self.testuser.id}/followers')
            self.assertEqual(res.status_code, 200)

            # Following page
            res = c.get(f'/users/{self.testuser.id}/following')
            self.assertEqual(res.status_code, 200)

            # Likes page
            res = c.get(f'/users/{self.testuser.id}/likes')
            self.assertEqual(res.status_code, 200)
