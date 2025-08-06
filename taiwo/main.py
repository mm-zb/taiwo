from recommender import recommend, add_id_to_df, df_to_matrix
from genius import lyric_to_url, get_songs, json_to_list
from spotify_auth import get_code, get_token, refresh_access
from spotify_requests import request_top_songs, clean_top_songs, request_top_artists

from flask import Flask, render_template, request, session, redirect
from flask_session import Session
from flask_mail import Mail, Message
import random, sqlite3, pickle
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random

client_id = 'id'
client_secret = 'secret'

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

class Graph: 
  #directed graph to form a friends network
  #using a directed graph, which makes it a following system rather than a friends system
  def __init__(self, existing=None):
    if existing:
      self.adjacency_list = existing
      #allows the graph to be stored in a text file, and then retrieved later
    else:
      self.adjacency_list = {}
      conn = sqlite3.connect('logins.db')
      c = conn.cursor()
      #creates empty adjacency list if no friends system in place
  
      c.execute('SELECT * FROM users')
      data = c.fetchall()
      #copies the database to a variable
      for account in data:
        self.adjacency_list[account[0]] = []
      #adds all users to the adjacency list, having no friends initially
      conn.close()

  def follow(self, user1, user2):
    self.adjacency_list[user1].append(user2)
    #user1 adds user2 as a friend 

  def unfollow(self, user1, user2):
    self.adjacency_list[user1].remove(user2)
    #user1 removes user2 as a friend

  def save(self):
    with open('friends_list.pkl', 'wb') as fh:
      pickle.dump(self.adjacency_list, fh)
    #writes current user data to a .pkl file

def register_account(email, user, pwd, cpwd):
    if not user or not pwd or not cpwd or not email:
        return 1
    #checks if all fields are filled out
    if cpwd != pwd:
        return 2
    #checks if password and confirm password have the same value
    if len(pwd) < 8 or len(pwd) > 16:
        return 4
    #checks if password is the correct length 

    conn = sqlite3.connect('logins.db')
    c = conn.cursor()

    c.execute("SELECT * FROM users")
    #executes SQL to copy the whole database
    data = c.fetchall()
    #assigns data to variable

    for i in data:
        if i[0] == user:
            return 3
    #checks if the username is already taken
    
    c.execute("INSERT INTO users VALUES (?,?,?,?,?)", (user, pwd, email, 'null', 'null'))
    #adds username, password and email to database if all checks passed

    conn.commit()
    conn.close()

    return 0

def correct_login(username, password):
    if not username or not password:
        return 2
    #checks if all fields are filled out

    conn = sqlite3.connect('logins.db')
    c = conn.cursor()

    c.execute('SELECT * FROM users')
    data = c.fetchall()
    #executes SQL to copy entire database to a variable

    conn.close()
    for i in range(len(data)):
        if data[i][0] == username:
            if data[i][1] == password:
                return 0
            #if the username and hashed password matches then log in
    return 1
    #no username, password combination found

def add_friend(friend):
    graph = Graph(session.get('friends', None))
    user = session.get('account', None)
    #assign the user's username, and the global friends list to variables

    conn = sqlite3.connect('logins.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    data = c.fetchall()
    #executes SQL to copy entire database to a variable

    usernames = []
    for i in data:
        usernames.append(i[0])
    conn.close()
    #adds usernames to a list

    if friend in graph.adjacency_list[user]:
        return str(user)+' is already following '+str(friend)
        #if already following the user entered
    elif friend not in usernames:
        return 'There is nobody with the username '+str(friend)
        #if the username is not taken
    else:
        graph.follow(user, friend)
        graph.save()
        session['friends'] = graph.adjacency_list
        return 'Followed '+str(friend)+' successfully'
        #if all checks passed, follow the user


app = Flask(__name__)
app.secret_key = 'secret'
#shh

app.config['SESSION_TYPE'] = 'memcached'
#allows for caching 

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'secret'
app.config['MAIL_PASSWORD'] = 'secret'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)
#email settings

sess = Session()
#setting up a session, to allow for sessionwide variables

@app.route('/')
def home():
    session['account'] = False
    return redirect('/index')

@app.route('/index', methods=['GET'])
def index_page():
    return redirect('/login')
    if request.method == 'GET':
        if len(request.url.split('=')) > 1:
            return render_template('index.html', song_name=get_random_song(request.url.split('=')[1]))
    return render_template('index.html', song_name='')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        u = request.form['username']
        p = (request.form['password']) 
        log = correct_login(u, p)
        if log==0:
            e = 'Logged into '+str(u)
            session['account'] = str(u)

            try:
                with open('friends_list.pkl', 'rb') as fh:
                    friends_list = pickle.load(fh) 
            except:
                friends_list = None
            session['friends'] = Graph(friends_list).adjacency_list
            return redirect('/account')
        elif log==1:
            e = 'Invalid Username or Password'
        else:
            e = 'Fill out all fields'
    else:
        e = ''    
    if session.get('account', None):
        return redirect('/account')
    return render_template('login.html', error_msg=e)

@app.route('/register', methods=['GET','POST'])
def register_page():
    if request.method == 'POST':
        email = request.form['email']
        user = request.form['username']
        pwd = (request.form['password'])
        cpwd = (request.form['conf_password'])
        reg = register_account(email, user, pwd, cpwd)
        if reg == 0:
            error = 'Registered Successfully'
            account = user
            try:
                with open('friends_list.pkl', 'rb') as fh:
                    friends_list = pickle.load(fh) 
            except:
                friends_list = None
            friends = Graph(friends_list)
            friends.adjacency_list[account] = []
            session['friends'] = friends.adjacency_list
            friends.save()
            session['account'] = account
            return redirect('/account')
        elif reg == 1:
            error = 'Fill out all fields'
        elif reg == 2:
            error = 'Ensure both password fields are the same'
        elif reg == 4:
            error = 'Password must be between 8 and 16 characters'
        else:
            error = 'Username taken'
    else:
        error = ''
        user = ''
        email = ''
        #if the user has not pressed submit yet, set all the pre-filled values to empty
    return render_template('register.html', error_msg=error, username=user, email=email)

@app.route('/lyrics', methods=['GET', 'POST'])
def lyrics_page():
    if request.method=='POST':
        lyric = request.form['lyrics']
        url = lyric_to_url(lyric)
        response = get_songs(url)
        songs = json_to_list(response)
        return render_template('lyrics.html', flag=True, songs=songs)
    return render_template('lyrics.html', flag=False)

@app.route('/recommend', methods=['GET', 'POST'])
def recommend_page():
    if request.args.get('id'):

        df = add_id_to_df(request.args.get('id'))
        #creates a dataframe, with all previous data, and the song found added on

        model = df_to_matrix(df)
        #converts the dataframe to a cosine similarity matrix
      
        songs = recommend(request.args.get('id'), model, df)
        #searches through the matrix to find the songs with the most similar values to it
      
        return render_template('recommend.html', flag=True, songs=songs)

    if request.method == 'POST':
        name = request.form['song-name']
        if name.strip() == '':
            name = '.'
        search = sp.search(q=name, type='track')
        results = []
        n = len(search['tracks']['items'])
        if n > 9:
            n = 10
        for i in range(n):
            artist = search['tracks']['items'][i]['artists'][0]['name']
            title = search['tracks']['items'][i]['name']
            id = search['tracks']['items'][i]['id']
            results.append((title, artist, id))

        return render_template('recommend.html', flag=False, results=results)
    return render_template('recommend.html', flag=False, results=None)

@app.route('/stats')
def stats_page():
    username = session.get('account', None)
    #get username logged in

    if not username:
        return redirect('/login')
    #redirects to login
    
    if request.args.get('friend'):
        username = request.args.get('friend')
        #change username so that the friend's information can be gotten

    conn = sqlite3.connect('logins.db')
    c = conn.cursor()
    statement = "SELECT * FROM users WHERE username = '"+username+"'"
    c.execute(statement)
    data = c.fetchall()[0]
    #get all of the logged in users data 

    if data[3] == 'null':
        return render_template('stats.html', username=True, token=False)
    #tells the user to connect their spotify account if it is not connected

    refresh_access(username)
    #resets permissions in case timer has expired

    top_song_data = request_top_songs(data[3])
    top_artist_data = request_top_artists(data[3])
    #runs the API request to get the data

    top_songs = list()
    for i in range(10):
        artist = top_song_data['items'][i]['artists'][0]['name']
        name = top_song_data['items'][i]['name']
        spotify_link = top_song_data['items'][i]['external_urls']['spotify']
        album_cover = top_song_data['items'][i]['album']['images'][0]['url']
        if '(' in name:
            index = name.index('(')
            name = name[:index]
        #cleans name to remove any brackets
        top_songs.append((name,artist,spotify_link,album_cover))
    #adds the appropriate data for each song to a list

    top_artists = list()
    for i in range(5):
        name = top_artist_data['items'][i]['name']
        spotify_link = top_artist_data['items'][i]['external_urls']['spotify']
        artist_image = top_artist_data['items'][i]['images'][2]['url']
        top_artists.append((name,spotify_link,artist_image))
    #adds the appropriate data for each artist to a list

    friends=session.get('friends', None)[session.get('account', None)]
    #gets the friends of the account currently logged in
    #does not use the username variable, as this changes if viewing a friend's stats
    return render_template('stats.html', username=True, token=True, songs=top_songs, artists=top_artists, genre=top_artist_data['items'][0]['genres'][0], friends=friends)

@app.route('/generate', methods=['GET', 'POST'])
def generate_page():
    username = session.get('account', None)
    #get username logged in

    if not username:
        return redirect('/login')
    #redirects to login

    refresh_access(username)
    #refreshes spotify API token

    conn = sqlite3.connect('logins.db')
    c = conn.cursor()
    statement = "SELECT * FROM users WHERE username = '"+username+"'"
    c.execute(statement)
    data = c.fetchall()[0]
    #get all of the logged in users data 

    if data[3] == 'null':
        return render_template('generate.html', username=True, token=False)
    #tells the user to connect their spotify account if it is not connected 
    if request.method == 'POST':
        token = data[3]
        data = (request_top_songs(token))
        songs = clean_top_songs(data)
        #get user data from spotify

        feature_columns = ['danceability',
                            'energy',
                            'speechiness',
                            'instrumentalness',
                            'valence',
                            'tempo',
                            'popularity']
        profile = {}
        for feature in feature_columns:
            profile[feature] = 0
        #set up an empty row for the database

        for song in songs:
            profile['popularity'] += song[3]

            audio_features = sp.audio_features(song[0])[0]
            for feature in feature_columns[:-1]:
                profile[feature] += audio_features[feature]
        #add up the total stats for each of the users top 30 songs

        for key in profile.keys():
            profile[key] = round((profile[key]/30),3)
        #divide each stat by 30 (to average them), making a taste profile
            
        profile['artist'] = 'playlist'
        profile['song_title'] = 'playlist'
        profile['track_id'] = 'playlist'
        profile_df = pd.DataFrame(profile, index = [0])
        #sets a placeholder name, artist and id to make the data easy to find & remove later

        df = pd.read_csv('csv/data.csv')
        df = pd.concat([df,profile_df], ignore_index=True)
        mat = df_to_matrix(df)
        #joins the taste profile to existing song data

        playlist = recommend('playlist',mat,df, 30)
        #runs the recommendation and produces a list of 30 recommended songs

        return render_template('generate.html', username=True, token=True, run=True ,songs=playlist)
    return render_template('generate.html', username=True, token=True, run=False)

@app.route('/account', methods=['GET', 'POST'])
def account_page():
    username = session.get('account', None)
    if request.method == 'POST':
        response=[]
        #create empty list of potential responses
        if request.form['new_email']:
            #if added an email

            conn = sqlite3.connect('logins.db')
            c = conn.cursor()
            statement = "UPDATE users SET email = '"+request.form['new_email']+"' WHERE username = '"+username+"'"
            #copy email to database

            c.execute(statement)
            conn.commit()
            conn.close()
            response.append('Saved email successfully')
            #add appropriate response

        if request.form['current_password']:
            #if tried to change password
            conn = sqlite3.connect('logins.db')
            c = conn.cursor()
            statement = "SELECT * FROM users WHERE username = '"+username+"'"
            c.execute(statement)
            data = c.fetchall()[0]
            #get the user's current password
            
            if request.form['current_password'] == data[1]: 
                #if they have entered their current passwords correct
                if request.form['new_password']==request.form['confirm_password']:
                    #if the two entered passwords match
                    statement = "UPDATE users SET password = '"+request.form['new_password']+"' WHERE username = '"+username+"'"
                    c.execute(statement)
                    conn.commit()
                    conn.close()
                    #update the database with their new password
                    response.append('Saved password successfully')
                else:
                    response.append('New passwords are different')
            else:
                response.append('Wrong password')
            #add appropriate repsonses

        conn = sqlite3.connect('logins.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = '"+username+"'")
        data = c.fetchall()[0]
        conn.close()
        #runs regardless of whether they have changed their details or not
        #gets the users email to prefill the entry

        return render_template('account.html', account=username, current_email=data[2], response=', '.join(response))
    if username:
        conn = sqlite3.connect('logins.db')
        c = conn.cursor()
        statement="SELECT * FROM users WHERE username = '"+username+"'"
        c.execute(statement)
        data = c.fetchall()[0]
        conn.close()
        
        return render_template('account.html', account=username, current_email=data[2])
    return render_template('account.html', account=username)

@app.route('/friends', methods=['GET', 'POST'])
def friends_page():
    if request.method == 'POST':
        e = add_friend(request.form['friend-username'])
    else:
        e = ''
    username = session.get('account', None)
    if username:
        return render_template('friends.html', account=username, error_msg=e, friends=session.get('friends', None)[session.get('account', None)])
    else:
        return render_template('friends.html', account=username, error_msg=e, friends=None)

@app.route('/logout')
def logout_page():
    return redirect('/')

@app.route('/unfollow')
def unfriend_method():
    graph = Graph(session.get('friends', None))
    #get the adjacency list of friends

    graph.unfollow(session.get('account', None), request.args.get('user'))
    #call the graph data structure's method to unfollow someone

    graph.save()
    session['friends'] = graph.adjacency_list
    #save changes and copy it to the session variable
    return redirect('/friends')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        #if the user presses submit

        email = request.form['email']
        #gets the email that the user entered

        conn = sqlite3.connect('logins.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = '"+email+"'")
        data = c.fetchall()
        #executes SQL to get accounts where email matches

        if data:
            digits = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890'
            password = ''.join([random.choice(digits) for i in range(10)])
            #if there is an account, generate a random 10 digit string as a password

            account = data[0][0]

            msg = Message('Your new password', sender='nea.recommendation.app@gmail.com', recipients=[email])
            msg.body = "Hey, "+account+"!\nYou reset your password on Zayan's NEA.\n\n Your new password is:\t"+password+"\n\nEnjoy using our app!"
            mail.send(msg)
            #email the user with their new password

            statement = "UPDATE users SET password = '"+password+"' WHERE username = '"+account+"'"
            c.execute(statement)
            conn.commit()
            #update the user's password to the random string
            status = 'Password reset! Check your email'
        else:
            status = "Sorry, we couldn't find that email"
            #if not found, return appropriate message
        conn.close()
        return render_template('forgot.html', error_msg=status)
    return render_template('forgot.html', error_msg='')

@app.route('/spotify')
def spotify_page():
    get_code()
    return redirect('/account')

@app.route('/callback')
def callback():
    code = request.url.split('=')[1]
    #get code
    tokens = get_token(code)
    #get token
    user = session.get('account', None)

    conn = sqlite3.connect('logins.db')
    c = conn.cursor()
    statement = "UPDATE users SET access_token = '"+tokens[0]+"' WHERE username = '"+user+"'"
    #copy access token to database

    c.execute(statement)
    statement = "UPDATE users SET refresh_token = '"+tokens[1]+"' WHERE username = '"+user+"'"
    #copy refresh token to database

    c.execute(statement)
    conn.commit()
    conn.close()
    return redirect('/login')



@app.route('/debug')
def debug():
    #insert code that needs to run here
    return redirect('/')

if __name__=='__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=80)
