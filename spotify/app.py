''' Example of Spotify authorization code flow (refreshable user auth).

Displays profile information of authenticated user and access token
information that can be refreshed by clicking a button.

Basic flow:
    -> '/'
    -> Spotify login page
    -> '/callback'
    -> get tokens
    -> use tokens to access API

Required environment variables:
    FLASK_APP, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SECRET_KEY

More info:
    https://developer.spotify.com/documentation/general/guides/authorization-guide/#authorization-code-flow

'''
import os
if int(os.environ.get('DEBUG')) == 1:
    debug = True
else:
    debug = False
  # when i run locally True, when I deploy it False

from flask import (
    abort,
    Flask,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
    flash,
)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from flask_talisman import Talisman
import json
import requests
import secrets
import string
from urllib.parse import urlencode
import spotipy
import datetime
from datetime import datetime
import redis
import os
import json
from oauthlib.oauth2 import WebApplicationClient
from user import User
import random
import spotipy.util as util



GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

black_image_url = "https://images.unsplash.com/photo-1548697143-6a9dc9d9d80f?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8Mnx8YmxhY2slMjBzY3JlZW58ZW58MHx8MHx8&w=1000&q=80"


# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)


r = redis.from_url(os.environ.get("REDIS_URL"))

# Client info
CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")

if debug:
    REDIRECT_URI = 'http://127.0.0.1:5000/callback'
else:
    REDIRECT_URI = 'https://www.yalewrappd.com/callback'

# Spotify API endpoints
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
ME_URL = 'https://api.spotify.com/v1/me'

# Start 'er up
app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET_KEY")
#Talisman(app)


login_manager = LoginManager(app)
#login_manager.init_app(app)
Talisman(app, content_security_policy=None)
#Talisman(app)

scope = 'user-library-read user-top-read playlist-modify-public'

username = 'bearsyankees'


#track_dict = {}
playlist_id="57IF8qCfvZTi06QQHqvYIv"
#r.mset({"tracks": json.dumps(track_dict)})
#print(json.loads(r.mget("tracks")[0].decode()).get("song2"))


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route("/")
def indexG():
    if session.get('auth') or debug:
        return render_template('index.html')
        #return "dubs" """"(
            #"<p>Hello, {}! You're logged in! Email: {}</p>"
           # "<div><p>Google Profile Picture:</p>"
           # '<img src="{}" alt="Google profile pic"></img></div>'
           # '<a class="button" href="/logout">Logout</a>'.format(
           #     current_user.name, current_user.email, current_user.profile_pic
           # )
       # )"""
    else:
        return render_template('indexG.html')

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route("/loginG")
def loginG():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/loginG/callback")
def callbackG():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    # Begin user session by logging the user in
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    user = User(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    )
    # Send user back to homepage
    if "@yale.edu" in userinfo_response.json()["email"]:
        login_user(user)
        session['auth'] = True
        print("email:", userinfo_response.json()["email"])
        r.mset({userinfo_response.json()["email"]: str(True)})
        return redirect(url_for("indexG"))
    else:
        return "sorry not a yale email"


"""@app.route('/')
def index():
    return render_template('index.html')"""

@app.route("/logoutG")
@login_required
def logoutG():
    logout_user()
    return redirect(url_for("indexG"))





@app.route('/<loginout>')
def login(loginout):
    '''Login or logout user.

    Note:
        Login and logout process are essentially the same.  Logout forces
        re-login to appear, even if their token hasn't expired.
    '''

    # redirect_uri can be guessed, so let's generate
    # a random `state` string to prevent csrf forgery.
    state = ''.join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16)
    )

    # Request authorization from user
    scope = "user-read-private user-top-read"

    if loginout == 'logout':
        payload = {
            'client_id': CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'state': state,
            'scope': scope,
            'show_dialog': True,
        }
    elif loginout == 'login':
        payload = {
            'client_id': CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'state': state,
            'scope': scope,
        }
    else:
        abort(404)

    res = make_response(redirect(f'{AUTH_URL}/?{urlencode(payload)}'))
    res.set_cookie('spotify_auth_state', state)

    return res


@app.route('/callback')
def callback():
    error = request.args.get('error')
    code = request.args.get('code')
    state = request.args.get('state')
    stored_state = request.cookies.get('spotify_auth_state')

    # Check state
    if state is None or state != stored_state:
        app.logger.error('Error message: %s', repr(error))
        app.logger.error('State mismatch: %s != %s', stored_state, state)
        abort(400)

    # Request tokens with code we obtained
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }

    # `auth=(CLIENT_ID, SECRET)` basically wraps an 'Authorization'
    # header with value:
    # b'Basic ' + b64encode((CLIENT_ID + ':' + SECRET).encode())
    res = requests.post(TOKEN_URL, auth=(CLIENT_ID, CLIENT_SECRET), data=payload)
    res_data = res.json()

    if res_data.get('error') or res.status_code != 200:
        app.logger.error(
            'Failed to receive token: %s',
            res_data.get('error', 'No error information received.'),
        )
        abort(res.status_code)

    # Load tokens into session
    session['tokens'] = {
        'access_token': res_data.get('access_token'),
        'refresh_token': res_data.get('refresh_token'),
    }

    return redirect(url_for('me'))


@app.route('/refresh')
def refresh():
    '''Refresh access token.'''

    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': session.get('tokens').get('refresh_token'),
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    res = requests.post(
        TOKEN_URL, auth=(CLIENT_ID, CLIENT_SECRET), data=payload, headers=headers
    )
    res_data = res.json()

    # Load new token into session
    session['tokens']['access_token'] = res_data.get('access_token')

    return json.dumps(session['tokens'])



@app.route('/me')
def me():
    if session.get('auth') or debug:
        token = util.prompt_for_user_token(username, scope)
        if token:
            sp1 = spotipy.Spotify(auth=token)
            current = sp1.user_playlist_tracks(playlist_id=playlist_id)
            c_b = [track['track']['id'] for track in current['items']]
            #print(c_b)
        else:
            return "we got a problem"
        sp = spotipy.Spotify(auth=session['tokens'].get('access_token'))
        top_artists = sp.current_user_top_artists(limit=50)
        top_tracks = sp.current_user_top_tracks(limit=50)
        track_ids = [track['id'] for track in top_tracks['items'] if track['id'] not in c_b]
        if r.get(sp.me()["id"]) is None:
            r.mset({sp.me()["id"]: json.dumps(top_artists['items'])})
            for i, item in enumerate(top_artists['items']):
                if r.get(item['name']) is None:
                    r.mset({item['name']: (50-i)})
                else:
                    r.incrby(item['name'], 50-i)
                #print(i, item['name'], item['genres'])
            if (r.get("tracks")) is None:
                already_tracks = {}
            else:
                already_tracks = json.loads(r.mget("tracks")[0].decode())
            for i, id in enumerate(track_ids):
                if already_tracks.get(id):
                    already_tracks[id] += 50-i
                else:
                    already_tracks[id] = 50-i
            r.mset({"tracks": json.dumps(already_tracks)})
            #print("here",r.mget("tracks"))
            for track in track_ids[0:5]:
                if track not in c_b:
                    results = sp1.user_playlist_add_tracks(username, playlist_id, [track])
                    print(results)
                    break
                else:
                    pass
                    #print(track, "already in")
        else:
            pass
            #print("already in")

        #print(r.keys())
        #print(sp.me()["id"])
        artists = []
        #print(top_artists['items'])
        for i, item in enumerate(top_artists['items']):
            try:
                artists.append([i + 1, item['name'], item['images'][0]['url'], item['popularity']])
            except:
                #print(i, item)
                artists.append([i + 1, item['name'], black_image_url, item['popularity']])
        #print(artists)
        try:
            most_pop_for_quip = random.choice(sorted([artist for artist in artists[:10] if artist[1] != "Kanye West"], key=lambda t: t[3], reverse=True)[0:3])[1]
        except:
            return "inactive spotify"
        #print(most_pop_for_quip)
        quips = ["As basic as it comes.", "You like {} too? No way.".format(most_pop_for_quip),
                 "I've seen better artists on my mom's Spotify Wrapped.", "You must be in JE.", "This looks like the Woads setlist."]
        random_quip = random.choice(quips)
        #print(r.get("tracks"))
        return render_template("presentUserHoriz.html", artists=artists, random_quip=random_quip)
    else:
        return "nope u cant access this please try again and login with a Yale email!"

PASSPHRASE = os.environ.get("passphrase")
def password_prompt_data(message):
    return f'''
                <form action="/data" method='post'>
                  <label for="password">{message}:</label><br>
                  <input type="password" id="password" name="password" value=""><br>
                  <input type="submit" value="Submit">
                </form>'''

def password_prompt_graph(message):
    return f'''
                <form action="/graph" method='post'>
                  <label for="password">{message}:</label><br>
                  <input type="password" id="password" name="password" value=""><br>
                  <input type="submit" value="Submit">
                </form>'''

def password_prompt_song(message):
    return f'''
                <form action="/songData" method='post'>
                  <label for="password">{message}:</label><br>
                  <input type="password" id="password" name="password" value=""><br>
                  <input type="submit" value="Submit">
                </form>'''


@app.route('/data', methods=['GET', 'POST'])
def data():
    if request.method == 'GET':
        return password_prompt_data("Admin password:")
    elif request.method == 'POST':
        if request.form['password'] != PASSPHRASE:
            return password_prompt_data("Invalid password, try again. Admin password:")
        else:
            for key in r.keys():
                pass
                #print(key.decode("utf-8"))
            #print(json.dumps(list(map(lambda n: (n.decode("utf-8"), r.get(n).decode("utf-8")), r.keys()))))
            #return "poop"
            #return json.dumps(list(map(lambda n: (n.decode("utf-8"), r.get(n).decode("utf-8")) if r.get(n).decode("utf-8").isdigit() else None, r.keys())))

            return json.dumps(sorted(list(map(lambda n: (n.decode("utf-8"), r.get(n).decode("utf-8")) if r.get(n).decode("utf-8").isdigit() else None, r.keys())),key = lambda x: int(x[1]) if x else 0, reverse = True))

@app.route('/graph' , methods=['GET', 'POST'])
def graph():
    if request.method == 'GET':
        return password_prompt_graph("Admin password:")
    elif request.method == 'POST':
        if request.form['password'] != PASSPHRASE:
            return password_prompt_graph("Invalid password, try again. Admin password:")
        else:
            if 1 == 2: # debug:
                names = ['Kanye West', 'Taylor Swift', 'Lana Del Rey', 'ROSALÍA', 'Kendrick Lamar', 'Mac Miller', 'Big Thief', 'Steve Lacy', 'Japanese Breakfast', 'Elliott Smith', 'Harry Styles', 'Bad Bunny', 'Lorde', 'Drake', 'Angel Olsen', 'Frank Ocean', 'Charli XCX', 'Beyoncé', 'The Beatles', 'Tyler, The Creator', '070 Shake', 'Radiohead', 'Father John Misty', 'Remi Wolf', 'Djo', 'Lizzy McAlpine', 'Playboi Carti', 'Fiona Apple', 'Miley Cyrus', 'Adrianne Lenker', 'Emile Mosseri', 'Lucy Dacus', 'The 1975', 'Chance the Rapper', 'Vampire Weekend', 'Simon & Garfunkel', 'Weyes Blood', 'Nina Simone', 'Bruno Mars', 'Lupe Fiasco', 'Labrinth', 'C. Tangana', 'Sufjan Stevens', 'beabadoobee', 'Mimi Webb', 'The Regrettes', 'Natalia Lafourcade', 'Cher', 'Tame Impala', 'The Beach Boys', 'Quarteto Em Cy', 'SIX', 'Soccer Mommy', 'The Rolling Stones', 'Amy Winehouse', 'Smino', 'Phoebe Bridgers', 'James Blake', 'J Balvin', 'Joey Bada$$', 'AJR', 'MIKA', 'Adele', 'Leikeli47', 'Calvin Harris', 'Bon Iver', 'Max Richter', 'Pusha T', 'Grateful Dead', 'Superorganism', 'Rauw Alejandro', 'Shania Twain', 'Eminem', 'Travis Scott', 'Pink Floyd', 'Elton John', 'Kid Cudi', 'Snail Mail', 'Fleet Foxes', 'Billie Eilish', 'Joy Crookes', 'Hans Zimmer', 'KAYTRANADA', 'Kota the Friend', 'Clairo', 'Post Malone', 'Rihanna', 'Billie Marten', 'Indigo De Souza', 'Kacey Musgraves', 'The Alchemist', 'The Velvet Underground', 'Saba', 'Rainbow Kitten Surprise', 'Gipsy Kings', 'Stormzy', 'Silvana Estrada', 'Vivaldi Piano Project', 'Perfume Genius', 'Mojave 3', 'Maude Latour', 'Lil Uzi Vert', 'Kelly Clarkson', 'Dry Cleaning', 'Alex G', 'Silvio Rodríguez', 'Anderson .Paak', 'Florist', 'Caamp', 'Childish Gambino', 'Whitney', 'Moses Sumney', 'A$AP Rocky', 'FKA twigs', 'Take That', 'Rodrigo Amarante', 'Faye Webster', 'David Bowie', 'Christian Lee Hutson', 'Omer Adam', 'Harry Nilsson', 'Guitarricadelafuente', 'DJ Khaled', 'Lil Tjay', 'The Coup', 'Tomppabeats', 'Florence + The Machine', 'Polo & Pan', 'Belle and Sebastian', 'Dean Martin', 'Death Cab for Cutie', 'The Doors', 'AJ Tracey', 'El Alfa', 'Dijon', 'Central Cee', 'Rex Orange County', 'alt-J', 'SZA', 'John Lennon', 'Courtney Barnett', 'Miguel', 'J. Cole', 'Ethel Cain', 'Steely Dan', 'Mac DeMarco', 'Jerry Garcia', 'Birdy', 'Genesis Owusu', 'Mt. Joy', 'Katy Perry', 'Las Ketchup', 'Alan Silvestri', 'Sofi Tukker', 'New Order', 'Matty Wood$', 'Dave', 'The Japanese House', 'Eydie Gormé', 'NxWorries', 'Coldplay', 'Stevie Wonder', 'Blood Orange', 'Bob Dylan', 'The Strokes', 'ABBA', 'Enrique Iglesias', 'ROLE MODEL', 'JAY-Z', 'Sudan Archives', 'Still Woozy', 'redveil', 'Julien Baker', 'Bladee', 'LUCKI', 'Dominic Fike', 'Wiley Beckett', 'Automatic', 'Jonny Greenwood', 'Paul Simon', 'Toro y Moi', 'Alanis Morissette', 'Yung Lean', 'Green Day', 'Thundercat', 'Girlpool', 'Michael Jackson', 'Rita Payés', 'Daft Punk', 'The Wallflowers', 'Zusha', 'Andrew Bird', 'Kali Uchis', 'Fleetwood Mac', 'Gorillaz', 'Nena', 'Joan Baez', 'Billy Ocean', 'Amantina', 'The Lumineers', 'Brian Eno', "Noel Gallagher's High Flying Birds", 'Channel Tres', 'Wiz Khalifa', 'Flo Rida', 'Parquet Courts', 'Funkadelic', 'Treekoo', 'Ravid Plotnik', 'Olivia Dean', 'Peter McPoland', 'Scouting For Girls', 'HAIM', 'COBRAH', 'Supertramp', 'Sir Chloe', 'Daddy Yankee', 'Babe Rainbow', 'Rae Sremmurd', 'Bruce Springsteen', 'reggie', 'Gavin DeGraw', 'Omar Apollo', 'Kesha', 'Kaitlyn Aurelia Smith', 'JID', 'Phoenix', 'Ben Platt', 'FrankJavCee', 'Lake Street Dive', 'Tove Lo', 'Baby Keem', 'Ramin Djawadi', 'Hannah Montana', 'Nick Drake', 'Lil Nas X', 'Madonna', 'Cage The Elephant', 'Chuki Beats', 'Fabiano do Nascimento', '5 Seconds of Summer', 'Ronan Keating', 'Wet Leg', 'Beach House', 'Meek Mill', 'Miles Davis', 'Leona Lewis', 'Gustavo Cerati', 'Otis Redding']
                numbers = ['229', '209', '194', '186', '157', '151', '150', '148', '120', '120', '98', '97', '95', '93', '89', '88', '87', '87', '86', '83', '81', '77', '73', '71', '68', '68', '67', '67', '67', '65', '65', '63', '62', '57', '56', '56', '54', '54', '51', '49', '49', '49', '49', '49', '48', '48', '48', '47', '47', '46', '46', '46', '46', '46', '45', '45', '45', '45', '44', '44', '44', '44', '43', '43', '43', '43', '42', '42', '42', '42', '42', '42', '41', '41', '41', '40', '40', '40', '40', '40', '40', '39', '39', '39', '39', '39', '38', '38', '38', '38', '38', '37', '37', '37', '37', '37', '36', '36', '35', '35', '35', '35', '35', '35', '34', '34', '34', '33', '33', '33', '32', '32', '32', '32', '31', '31', '31', '31', '31', '31', '30', '30', '30', '30', '29', '29', '29', '28', '28', '28', '28', '27', '27', '27', '26', '26', '26', '26', '25', '25', '25', '25', '25', '25', '24', '24', '23', '23', '23', '23', '22', '22', '22', '22', '21', '21', '21', '21', '20', '20', '20', '19', '19', '19', '19', '19', '19', '18', '18', '18', '18', '17', '17', '17', '16', '16', '16', '16', '16', '15', '15', '15', '15', '15', '14', '14', '14', '14', '13', '13', '13', '13', '13', '12', '12', '12', '12', '12', '11', '11', '11', '11', '11', '10', '10', '10', '10', '10', '9', '9', '9', '9', '9', '9', '8', '8', '8', '8', '8', '7', '7', '7', '7', '6', '6', '6', '5', '5', '5', '4', '4', '4', '4', '4', '4', '4', '3', '3', '3', '3', '2', '2', '2', '2', '2', '1', '1', '1', '1']
            else:
                data = sorted(list(map(lambda n: (n.decode("utf-8"), r.get(n).decode("utf-8")) if r.get(n).decode("utf-8").isdigit() else None, r.keys())),key = lambda x: int(x[1]) if x else 0, reverse = True)
                #print(data)
                names = [item[0] for item in data if item is not None]
                numbers = [item[1] for item in data if item is not None]
                #print(names)
                #print(numbers)
            return render_template("graph.html",names=names[:40], numbers=numbers[:40])


@app.route('/songData', methods=['GET', 'POST'])
def sd():
    if request.method == 'GET':
        return password_prompt_song("Admin password:")
    elif request.method == 'POST':
        if request.form['password'] != PASSPHRASE:
            return password_prompt_song("Invalid password, try again. Admin password:")
        else:
            songs = json.loads(r.mget("tracks")[0].decode('utf8'))
            songs = (sorted(songs.items(), key = lambda x: int(x[1]), reverse=True))[0:50]
            token = util.prompt_for_user_token(username, scope)
            track_res = []
            if token:
                sp1 = spotipy.Spotify(auth=token)
                for i, track in enumerate(songs):
                    track_f = sp1.track(track_id=track[0])
                    #print(track_f)
                    track_res.append([i + 1, "{} -- {}".format(track_f["name"],track_f["artists"][0]["name"]),track[1]])
            return track_res

if debug:
    pass
    """@app.route('/flush')
    def flush():
        r.flushdb()
        return "flushed"""

    """
 @app.route('/data')
    def data():
        for key in r.keys():
            print(key.decode("utf-8"))
        #print(json.dumps(list(map(lambda n: (n.decode("utf-8"), r.get(n).decode("utf-8")), r.keys()))))
        #return "poop"
        #return json.dumps(list(map(lambda n: (n.decode("utf-8"), r.get(n).decode("utf-8")) if r.get(n).decode("utf-8").isdigit() else None, r.keys())))

        return json.dumps(sorted(list(map(lambda n: (n.decode("utf-8"), r.get(n).decode("utf-8")) if r.get(n).decode("utf-8").isdigit() else None, r.keys())),key = lambda x: int(x[1]) if x else 0, reverse = True))

    @app.route('/graph')
    def graph():
        if 1 == 2: # debug:
            names = ['Kanye West', 'Taylor Swift', 'Lana Del Rey', 'ROSALÍA', 'Kendrick Lamar', 'Mac Miller', 'Big Thief', 'Steve Lacy', 'Japanese Breakfast', 'Elliott Smith', 'Harry Styles', 'Bad Bunny', 'Lorde', 'Drake', 'Angel Olsen', 'Frank Ocean', 'Charli XCX', 'Beyoncé', 'The Beatles', 'Tyler, The Creator', '070 Shake', 'Radiohead', 'Father John Misty', 'Remi Wolf', 'Djo', 'Lizzy McAlpine', 'Playboi Carti', 'Fiona Apple', 'Miley Cyrus', 'Adrianne Lenker', 'Emile Mosseri', 'Lucy Dacus', 'The 1975', 'Chance the Rapper', 'Vampire Weekend', 'Simon & Garfunkel', 'Weyes Blood', 'Nina Simone', 'Bruno Mars', 'Lupe Fiasco', 'Labrinth', 'C. Tangana', 'Sufjan Stevens', 'beabadoobee', 'Mimi Webb', 'The Regrettes', 'Natalia Lafourcade', 'Cher', 'Tame Impala', 'The Beach Boys', 'Quarteto Em Cy', 'SIX', 'Soccer Mommy', 'The Rolling Stones', 'Amy Winehouse', 'Smino', 'Phoebe Bridgers', 'James Blake', 'J Balvin', 'Joey Bada$$', 'AJR', 'MIKA', 'Adele', 'Leikeli47', 'Calvin Harris', 'Bon Iver', 'Max Richter', 'Pusha T', 'Grateful Dead', 'Superorganism', 'Rauw Alejandro', 'Shania Twain', 'Eminem', 'Travis Scott', 'Pink Floyd', 'Elton John', 'Kid Cudi', 'Snail Mail', 'Fleet Foxes', 'Billie Eilish', 'Joy Crookes', 'Hans Zimmer', 'KAYTRANADA', 'Kota the Friend', 'Clairo', 'Post Malone', 'Rihanna', 'Billie Marten', 'Indigo De Souza', 'Kacey Musgraves', 'The Alchemist', 'The Velvet Underground', 'Saba', 'Rainbow Kitten Surprise', 'Gipsy Kings', 'Stormzy', 'Silvana Estrada', 'Vivaldi Piano Project', 'Perfume Genius', 'Mojave 3', 'Maude Latour', 'Lil Uzi Vert', 'Kelly Clarkson', 'Dry Cleaning', 'Alex G', 'Silvio Rodríguez', 'Anderson .Paak', 'Florist', 'Caamp', 'Childish Gambino', 'Whitney', 'Moses Sumney', 'A$AP Rocky', 'FKA twigs', 'Take That', 'Rodrigo Amarante', 'Faye Webster', 'David Bowie', 'Christian Lee Hutson', 'Omer Adam', 'Harry Nilsson', 'Guitarricadelafuente', 'DJ Khaled', 'Lil Tjay', 'The Coup', 'Tomppabeats', 'Florence + The Machine', 'Polo & Pan', 'Belle and Sebastian', 'Dean Martin', 'Death Cab for Cutie', 'The Doors', 'AJ Tracey', 'El Alfa', 'Dijon', 'Central Cee', 'Rex Orange County', 'alt-J', 'SZA', 'John Lennon', 'Courtney Barnett', 'Miguel', 'J. Cole', 'Ethel Cain', 'Steely Dan', 'Mac DeMarco', 'Jerry Garcia', 'Birdy', 'Genesis Owusu', 'Mt. Joy', 'Katy Perry', 'Las Ketchup', 'Alan Silvestri', 'Sofi Tukker', 'New Order', 'Matty Wood$', 'Dave', 'The Japanese House', 'Eydie Gormé', 'NxWorries', 'Coldplay', 'Stevie Wonder', 'Blood Orange', 'Bob Dylan', 'The Strokes', 'ABBA', 'Enrique Iglesias', 'ROLE MODEL', 'JAY-Z', 'Sudan Archives', 'Still Woozy', 'redveil', 'Julien Baker', 'Bladee', 'LUCKI', 'Dominic Fike', 'Wiley Beckett', 'Automatic', 'Jonny Greenwood', 'Paul Simon', 'Toro y Moi', 'Alanis Morissette', 'Yung Lean', 'Green Day', 'Thundercat', 'Girlpool', 'Michael Jackson', 'Rita Payés', 'Daft Punk', 'The Wallflowers', 'Zusha', 'Andrew Bird', 'Kali Uchis', 'Fleetwood Mac', 'Gorillaz', 'Nena', 'Joan Baez', 'Billy Ocean', 'Amantina', 'The Lumineers', 'Brian Eno', "Noel Gallagher's High Flying Birds", 'Channel Tres', 'Wiz Khalifa', 'Flo Rida', 'Parquet Courts', 'Funkadelic', 'Treekoo', 'Ravid Plotnik', 'Olivia Dean', 'Peter McPoland', 'Scouting For Girls', 'HAIM', 'COBRAH', 'Supertramp', 'Sir Chloe', 'Daddy Yankee', 'Babe Rainbow', 'Rae Sremmurd', 'Bruce Springsteen', 'reggie', 'Gavin DeGraw', 'Omar Apollo', 'Kesha', 'Kaitlyn Aurelia Smith', 'JID', 'Phoenix', 'Ben Platt', 'FrankJavCee', 'Lake Street Dive', 'Tove Lo', 'Baby Keem', 'Ramin Djawadi', 'Hannah Montana', 'Nick Drake', 'Lil Nas X', 'Madonna', 'Cage The Elephant', 'Chuki Beats', 'Fabiano do Nascimento', '5 Seconds of Summer', 'Ronan Keating', 'Wet Leg', 'Beach House', 'Meek Mill', 'Miles Davis', 'Leona Lewis', 'Gustavo Cerati', 'Otis Redding']
            numbers = ['229', '209', '194', '186', '157', '151', '150', '148', '120', '120', '98', '97', '95', '93', '89', '88', '87', '87', '86', '83', '81', '77', '73', '71', '68', '68', '67', '67', '67', '65', '65', '63', '62', '57', '56', '56', '54', '54', '51', '49', '49', '49', '49', '49', '48', '48', '48', '47', '47', '46', '46', '46', '46', '46', '45', '45', '45', '45', '44', '44', '44', '44', '43', '43', '43', '43', '42', '42', '42', '42', '42', '42', '41', '41', '41', '40', '40', '40', '40', '40', '40', '39', '39', '39', '39', '39', '38', '38', '38', '38', '38', '37', '37', '37', '37', '37', '36', '36', '35', '35', '35', '35', '35', '35', '34', '34', '34', '33', '33', '33', '32', '32', '32', '32', '31', '31', '31', '31', '31', '31', '30', '30', '30', '30', '29', '29', '29', '28', '28', '28', '28', '27', '27', '27', '26', '26', '26', '26', '25', '25', '25', '25', '25', '25', '24', '24', '23', '23', '23', '23', '22', '22', '22', '22', '21', '21', '21', '21', '20', '20', '20', '19', '19', '19', '19', '19', '19', '18', '18', '18', '18', '17', '17', '17', '16', '16', '16', '16', '16', '15', '15', '15', '15', '15', '14', '14', '14', '14', '13', '13', '13', '13', '13', '12', '12', '12', '12', '12', '11', '11', '11', '11', '11', '10', '10', '10', '10', '10', '9', '9', '9', '9', '9', '9', '8', '8', '8', '8', '8', '7', '7', '7', '7', '6', '6', '6', '5', '5', '5', '4', '4', '4', '4', '4', '4', '4', '3', '3', '3', '3', '2', '2', '2', '2', '2', '1', '1', '1', '1']
        else:
            data = sorted(list(map(lambda n: (n.decode("utf-8"), r.get(n).decode("utf-8")) if r.get(n).decode("utf-8").isdigit() else None, r.keys())),key = lambda x: int(x[1]) if x else 0, reverse = True)
            print(data)
            names = [item[0] for item in data if item is not None]
            numbers = [item[1] for item in data if item is not None]
            print(names)
            print(numbers)
        return render_template("graph.html",names=names[:40], numbers=numbers[:40])"""

"""@app.route('/presentUser')
def present():
    sp = spotipy.Spotify(auth=session['tokens'].get('access_token'))
    top_artists = sp.current_user_top_artists(limit=50)
    artists = []
    print(top_artists['items'])
    for i, item in enumerate(top_artists['items']):
        artists.append([i + 1, item['name'], item['images'][0]['url'], item['popularity']])
    print(artists)
    most_pop_for_quip = random.choice(sorted(artists[:20], key=lambda t: t[3], reverse=True)[0:3])[1]
    print(most_pop_for_quip)
    quips = ["As basic as it comes.", "You like {} too? No way.".format(most_pop_for_quip),
             "I've seen better artists on my mom's Spotify Wrapped.", "You must be in JE."]
    random_quip = random.choice(quips)
    return render_template("presentUser.html", artists=artists, random_quip=random_quip)

"""



if debug:
    if __name__ == '__main__':
        app.run(debug=debug)#, ssl_context="adhoc")
else:
    if __name__ == '__main__':
        app.run()
