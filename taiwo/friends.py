import sqlite3
import pickle

class Graph: 
  #directed graph to form a friends network
  #using a directed graph, which makes it a following system rather than a friends system
  def __init__(self) -> None:
    try:
        with open('friends_list.pkl', 'rb') as fh:
            existing = pickle.load(fh)
        self.adjacency_list = existing
        #allows the graph to be stored in a .pkl file, and then retrieved later

    except FileNotFoundError as e:
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
