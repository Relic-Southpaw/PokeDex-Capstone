from flask import Flask, render_template, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
# import time, sys # for the delay function
import pokepy as pk

client = pk.V2Client()
app = Flask(__name__)

app.config['SECRET_KEY'] = "pokemonmeandyou"

# def delay_print(s):
#     """prints one letter at a time like the original games did"""
#     #found this tidbit on stack overflow
#     #https://stackoverflow.com/questions/9246076/how-to-print-one-character-at-a-time-on-one-line

#     for c in s:
#         sys.stdout.write(c)
#         sys.stdout.flush()
#         time.sleep(0.05)


# delay_print("hello world")
@app.route('/')
def search_pokemon():
    res = client.get_pokemon('1')
    ability = client.get_ability('1')
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
    # for x in list(res.stats):
    #     print (x.stat.name)

    return render_template ('base.html')
