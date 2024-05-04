import os
from flask import g, session
from app import app, session, CURR_USER_KEY, add_user_to_g
from unittest import TestCase
from models import connect_db, db, User

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///pokedex_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

db.drop_all()
db.create_all()

client = app.test_client()

class SetUser():
    """Testing the user loging for the app"""

    def __init__(self,username,password,email):
        self.username=username
        self.password=password
        self.email = email

form = SetUser(username = "test", 
                password = "PokemonRules01",
                email = "test@testing.com")

class TestUser(TestCase):
    """Tests user login and list"""
    def setUp(self):
        User.query.delete()
        user = User.signup(form.username, form.password,form.email)
        user.password = str(user.password)
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        """clean up and roll back user login"""

        db.session.rollback()

    def testPokemonList(self):
        """verifies user is logged in, and that the list pages is working"""
        resp = client.get('/pokemon/list/1',follow_redirects =True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("bulbasaur",html)

class PokemonAppTests(TestCase):
    """Testing front in HTML displays"""

    def test_home_page(self):
        resp = client.get('/')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<h1>Project: PokeDex</h1>', html)
    
    def test_pokemon_page(self):
        resp = client.get('/pokemon/25', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<H2>pikachu</H2>', html)