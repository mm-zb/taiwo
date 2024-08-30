## taiwo
# What?
A song recommendation tool web application, created primarily with Python, through Flask.
There are 4 features: Song Recommender, Playlist Generator, Lyric Searcher, and Stats Viewer.

# Why?
I made this program as part of my Computer Science A-level course. The Non-Examined Assessment structure of the course requires the student to make a program of any kind, and write a SDLC report about it. For this project and the report I received an A* with 66/70.

# How?
The main recommendation algorithm uses my own version of nearest neighbours, through turning each song into a vector with Spotify's "song features". The program then uses vector mathematics (from my A-level Further Mathematics course) to figure out which vectors are closest in angle, and then uses this rank all the songs in terms of similarity. This technique is called cosine similarity, and is used to compare one song to all of the others.

# Where?
To run the whole web app, install all files in the main folder (taiwo).
All Python libraries required are: Flask, SQLite, Pickle, Pandas, SpotiPy, NumPy, SKlearn. Any others you see are built into Python 3.
Then, run the file main.py.
You can either go to localhost on your browser, or the address given to you in the terminal.
**This app is not intended for significant use, and hence it is running on a development server still. This also means that you will need to use your own API keys, and replace any data I have replaced with 'secret'. 

# Who?
Taiwo is named after Taiwo Awoniyi, an inspiration for this project. As a striker, he is what they call "the full package". This completeness inspired this idea for one program that tailored to all music needs: song suggestions, finding songs by their lyrics, and viewing my own listening statistics - all in one app.

# Notes
Github did not like the size of the original csv file, so I had to make it more reasonable. For this, the song recommendations may be less than perfect.
A demonstration of how the app works can be found here: https://youtu.be/O6YQwn4OzvI?feature=shared
If you find any bugs or errors in my code, please do let me know: zayanbaig01@gmail.com
