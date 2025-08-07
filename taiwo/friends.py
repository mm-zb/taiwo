import sqlite3
import pickle

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
