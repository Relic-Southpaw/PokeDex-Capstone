import os

from flask import Flask, render_template, request, flash, redirect, session, g, abort, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import connect_db, db, User, PokeTeam
from forms import UserAddForm, LoginForm
# import time, sys # for the delay function
import pokepy as pk

client = pk.V2Client()
app = Flask(__name__)

CURR_USER_KEY = "curr_user"

app.config['SECRET_KEY'] = "pokemonmeandyou"
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///pokedex'))

connect_db(app)

# def delay_print(s):
#     """prints one letter at a time like the original games did"""
#     #found this tidbit on stack overflow
#     #https://stackoverflow.com/questions/9246076/how-to-print-one-character-at-a-time-on-one-line

#     for c in s:
#         sys.stdout.write(c)
#         sys.stdout.flush()
#         time.sleep(0.05)


# delay_print("hello world")
@app.route('/pokemon/<int:poke_id>')
def search_pokemon(poke_id):
    res = client.get_pokemon(poke_id)
    # print (res.name)
    # print (res.id)
    # for x in list(res.types):
    #     print (x.type.name)
    #     print (x.slot)
    # for x in list(res.abilities):
    #     print (x.ability.name)
    # print (res.height)
    # print (res.weight)
    # for x in list(res.moves):
    #     print (x.move.name)
    # print (res.species)

    return render_template ('pokedex_stats.html', pokemon = res)

@app.route('/')
def poke_search():
    # poke_id = 25
    return render_template ("home.html")

    #######################################################
    #Login / register / logout
    #######################################################

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    # IMPLEMENT THIS
    do_logout()
    flash("You have been logged out!")
    return redirect("/login")


@app.route('/register')
def signup():
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data
                )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)
    return render_template("/users/signup.html", form=form)

    #######################################################

@app.route('/pokemon/<int:poke_id>/abilities')
def poke_abilities_list(poke_id):
    '''gets a pokemon id, makes a list of abilities'''
    pokemon = client.get_pokemon(poke_id)
    abilities = []
    for a in list(pokemon.abilities):
        x = client.get_ability(a.ability.name)
        print(x.name)
        # for p in list(x.pokemon):
        #     print (p.pokemon)
        # print(list(x.pokemon))
        abilities.append(x)
        # loop to just add the english effects to the list
        for b in list(x.effect_entries):
            if b.language.name == 'en':
                x.effect = b.effect
    return render_template('poke_abilities.html', pokemon = pokemon, abilities = abilities)

@app.route('/pokemon/<int:poke_id>/moves')
def poke_moves_list(poke_id):
    pokemon = client.get_pokemon(poke_id)
    moves = []
    for m in list(pokemon.moves):
        moves.append(m)

    return render_template('poke_moves.html', pokemon = pokemon, moves = moves)

@app.route('/pokemon/moves/<move>')
def poke_move_def(move):
    move = client.get_move(move)

    return render_template('p_move_def.html', move = move)
