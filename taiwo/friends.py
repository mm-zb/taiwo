import sqlite3
import pickle
from flask import session

class Graph: 
  #directed graph to form a friends network
  #using a directed graph, which makes it a following system rather than a friends system
    def __init__(self) -> None:
        try:
            with open('friends_list.pkl', 'rb') as fh:
                existing = pickle.load(fh)
            self.adjacency_list = existing
            #allows the graph to be stored in a .pkl file, and then retrieved later

        except (EOFError, FileNotFoundError) as _:
            self.adjacency_list = {}
            with sqlite3.connect('logins.db') as conn:
                c = conn.cursor()
                #creates empty adjacency list upon initialisation (where no friends list is in place)
            
                c.execute('SELECT username FROM users')
                data = c.fetchall()
                #copies the database to a variable
                for account in data:
                    self.adjacency_list[account[0]] = []
                #adds all users to the adjacency list, having no friends initially
                
    def add_new_user(self, user: str) -> None:
        """
        Adds new user to graph when they register
        """
        self.adjacency_list[user] = []

    def follow(self, user1: str, user2: str) -> None:
        """
        Adds user2 to user1's friends
        """

        self.adjacency_list[user1].append(user2)

    def unfollow(self, user1: str, user2: str) -> None:
        """
        Removes user2 from user1's friends
        """
        self.adjacency_list[user1].remove(user2)

    def save(self) -> None:
        """
        Writes the graph to an external file, saving it 
        """

        with open('friends_list.pkl', 'wb') as fh:
            pickle.dump(self.adjacency_list, fh)

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

    with sqlite3.connect('logins.db') as conn:
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username = ?", (user))
        #executes SQL to copy the whole database
        data = c.fetchall()
        #assigns data to variable

        if data:
            return 3
        
        c.execute("INSERT INTO users VALUES (?,?,?,?,?)", (user, pwd, email, 'null', 'null'))
        #adds username, password and email to database if all checks passed

        conn.commit()

    return 0

def correct_login(username, password):
    if not username or not password:
        return 2
    #checks if all fields are filled out

    with sqlite3.connect("logins.db") as conn:
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        data = c.fetchall()
        #executes SQL to copy entire database to a variable

    if data:
        return 0
        #if the username and hashed password matches then log in
    return 1
    #no username, password combination found

def add_friend(friend):
    graph = Graph()
    user = session.get('account', None)
    #assign the user's username, and the session friends list to variables

    with sqlite3.connect('logins.db') as conn:
        c = conn.cursor()
        c.execute("SELECT usernames FROM users")
        data = c.fetchall()
        #executes SQL to copy usernames

    usernames = [d[0] for d in data]
    #extracts usernames from 1-tuples

    if friend in graph.adjacency_list[user]:
        return f"{user} is already following {friend}"
        #if already following the user entered
    elif friend not in usernames:
        return f"There is nobody with the username {friend}"
        #if the username is not taken
    else:
        graph.follow(user, friend)
        graph.save()
        session['friends'] = graph.adjacency_list
        return f"Followed {friend} successfully"
        #if all checks passed, follow the user