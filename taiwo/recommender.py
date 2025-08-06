import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import config

client_id = config.SPOTIFY_ID
client_secret = config.SPOTIFY_SECRET

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

df = pd.read_csv('csv/data.csv')
#reading in the data as a pandas dataframe from the csv

feature_columns = ['danceability',
                   'energy',
                   'speechiness',
                   'instrumentalness',
                   'valence',
                   'tempo',
                   'popularity']
#specifying the columns that will be used from the csv to calculate similarity

def df_to_matrix(df):
    scaler = MinMaxScaler()
    #transforms all values input between a certain range
    #like an activation function

    scaled_df = scaler.fit_transform(df[feature_columns])
    #changes all values of feature columns between 0 and 1
    #eg decibels changes froma negative nu mber to 0<=n<=1

    cosine_matrix = cosine_similarity(scaled_df)
    #this is where the calculations are done
    #each feature is combined and compared to the features of other songs
    #then a 'similarity value' is calculated for every pair of songs
    #each value is then placed in a matrix

    return cosine_matrix

def add_id_to_df(id):
    df = pd.read_csv('csv/data.csv')
    #gets the current songs from the csv, and stores in a pandas dataframe (df)
    if id in df['track_id'].to_list():
        return df
        #if the song is already in the dataframe, return the dataframe with no changes
    else:
        song = id_to_df(id)
        
        df = pd.concat([df,song], ignore_index=True)
        #combines the original dataframe with the new one (that is just the one song)
        df.drop(df.columns[0], axis=1).to_csv('csv/data.csv')
        #removes the duplicate index column
        return df

def id_to_df(id):
    track = sp.track(id)
    #gets the song data from the id using spotipy
  
    song_features = {}
    song_features['artist'] = track['artists'][0]['name']
    song_features['song_title'] = track['name']
    song_features['track_id'] = id
    song_features['popularity'] = track['popularity']
    #adds all of the song detail to a dictionary

    audio_features = sp.audio_features(id)[0]
    for feature in feature_columns[:-1]:
        song_features[feature] = audio_features[feature]
    #adds all of the recommendation features to the dictionary

    df = pd.DataFrame(song_features, index = [0])
    #creates a dataframe with just the song in

    return df

def recommend(song, model, df, n=10):
    indices = pd.Series(df.index, index=df['track_id']).drop_duplicates()
    #creates a pd.Series data structure
    #this is the same as a 1D array, but the indices can be anything
    #for this I made the indices the song id

    index = indices[song]
    #get the index of the song input in the matrix
    
    similarity = list(enumerate(model[index]))
    #get the similarity values of each song for the input
    #it then enumerates them, so gives each song a new index

    sorted_similarity = sorted(similarity, key = lambda x:x[1],reverse = True)
    #here the similarity values are sorted, in descending order
    #the key specifies how to sort the object
    #lambda in python is a way of making a function without using
    # def syntax. it follows the format arguments:expression
    # so here, the argument is the temp var x, and the lambda function
    # returns x[1], being the second object of x (if x is iterable).
    # so then this means that the list will be sorted by the second 
    # item in each tuple (because it has been enumerated).

    top_similarity = sorted_similarity[1:n+1]
    #gets the top 10 most similar songs.
    #first song ignored, as it will be the same as the input

    top_indices = [i[0] for i in top_similarity]
    #gets the indices put in by enumerate()

    top_titles = df['song_title'].iloc[top_indices]
    top_artists = df['artist'].iloc[top_indices]
    #gets the song names of the indices
    #iloc is a pandas function that gets specific values from 
    # a column in a dataframe
    
    top_titles = top_titles.tolist()
    top_artists = top_artists.tolist()
    #converts from a pandas series to a python list
    top=[]
    for i in range(n):
        top.append(top_titles[i]+' - '+top_artists[i])
    return top
