import os

from flask import Flask, render_template, request, flash, redirect, session, g, abort, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from .models import connect_db, db, User, PokeTeam, PokeFav
from .forms import UserAddForm, LoginForm, UserEditForm
import pokepy as pk

client = pk.V2Client()
app = Flask(__name__)

CURR_USER_KEY = "curr_user"

app.config['SECRET_KEY'] = "pokemonmeandyou"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///pokedex')
    # .replace('://', 'ql://', 1)
    )

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
    print (res.name)
    print (res.id)
    for x in list(res.types):
        print (x.type.name)
        print (x.slot)
    for x in list(res.abilities):
        print (x.ability.name)
    print (res.height)
    print (res.weight)
    for x in list(res.moves):
        print (x.move.name)
    print (res.species)

    return render_template ('pokedex_stats.html', pokemon = res)

@app.route('/')
def homepage():
    return render_template ("home.html")

@app.route('/poke-search')
def poke_search():
    ''' Searches for pokemon, 
    gets id, 
    and redirects to URL of specific pokemon.
    '''
    search = request.args.get('q')
    res = client.get_pokemon(search)
    pkid = res.id
    return redirect(f'/pokemon/{pkid}')

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


@app.route('/signup', methods=["GET", "POST"])
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

        return redirect("/")

    return render_template("/users/signup.html", form=form)

    #######################################################
    # User Information and profile

    #######################################################

@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""
    pk_favorites=[]
    user = User.query.get_or_404(user_id)
    favorites=user.favorites
    for fv in favorites:
        if fv.user_id == user_id:
            pokemon = client.get_pokemon(fv.poke_id)
            pk_favorites.append(pokemon)

    return render_template('users/detail.html', user=user, pk_favorites = pk_favorites)

@app.route('/users/profile', methods=["GET", "POST"])
def edit_profile():
    """Update profile for current user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = g.user
    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.username = form.username.data
            user.email = form.email.data

            db.session.commit()
            return redirect(f"/users/{user.id}")

        flash("Wrong password, please try again.", 'danger')

    return render_template('users/edit.html', form=form, user_id=user.id)

@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")
   

    #######################################################
    # Pokemon Interactions
    #######################################################

@app.route('/pokemon/list/<int:pg>')
def list_of_pokemon(pg):
    print(g.user.username)
    pokelist =[]
    y = (pg*100) +1
    if y > 1009:
        y = 1009 
    x = y - 100
    if y == 1009:
        x = 1001
    for p in range(x, y):
        pokemon = client.get_pokemon(p)
        pokelist.append(pokemon)
    return render_template('pklist.html', pklist = pokelist, pg = pg)

@app.route('/pokemon/list/<int:pg>/<int:poke_id>/like')
def like_from_list(pg, poke_id):
    print(pg)
    print (poke_id)
    if len(g.user.username)>1:
        PokeFav.addfavlist(
            user_id= g.user.id,
            poke_id = poke_id
            )
        db.session.commit()
    else:
        flash("You need to be logged in to do that!", 'danger')       
    return redirect(f'/pokemon/list/{pg}')

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

    #######################################################
    # error handling
    #######################################################

@app.errorhandler(500)
def page_not_found(e):
    """when the search fails it returns 500, so redirect for that"""

    return render_template('badsearch.html'), 500