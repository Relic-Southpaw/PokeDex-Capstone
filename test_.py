from unittest import TestCase
from flask import session
from app import app
from models import db, User

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///pokedex_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

db.drop_all()
db.create_all()

client = app.test_client()

class FrontEndTestCase(TestCase):
    """Testing front in HTML displays"""

    def test_home_page(self):
        resp = client.get('/')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<h1>Project: PokeDex</h1>', html)
    
    def test_pokemon_page(self):
        resp = client.get('/pokemon/25')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<h2>pikachu</h2>', html)



#This is test sample for testing logins and users
USER_1 = {

}

class PokemonUsersTestCase(TestCase):
    """Testing the user loging for the app"""

    def setUp(self):
        """Making demo data."""

    def tearDown(self):
        """Clearing test data"""
        db.session.rollback()