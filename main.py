from tkinter import *
from tkinter import messagebox
import os
from tkcalendar import DateEntry
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth

FG = "#2dec84"
FONT = ("Franklin Medium Gothic", 16, "bold")
START_URL = "https://www.billboard.com/charts/hot-100/"
SPOTIFY_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")

# spotipy code
spotify = spotipy.Spotify(
    auth_manager=SpotifyOAuth(client_id=SPOTIFY_ID,
                              client_secret=SPOTIFY_SECRET,
                              redirect_uri="http://example.com",
                              scope="playlist-modify-private",
                              show_dialog=True,
                              cache_path="token.txt"
                              )
)
user_id = spotify.current_user()["id"]


# search spotify for songs matching each song title and artist
def search_songs():
    top_100 = pull_songs()
    spotify_searches = []
    for song in top_100:
        try:
            result = spotify.search(q=f"track:{song} artist:{top_100[song]}", type="track", limit=1)
            # check if song title and artist match result
            if result["tracks"]["items"][0]["name"].lower() == song.lower() \
                    and top_100[song].lower() in result["tracks"]["items"][0]["artists"][0]["name"].lower():
                spotify_searches.append(result["tracks"]["items"][0]["id"])

        except IndexError:
            pass
    create_playlist(spotify_searches)


# create new playlist with 100 songs from chosen date
def create_playlist(song_list):
    date = calendar.get()
    name = f"{date} Billboard 100(ish)"
    new_playlist = spotify.user_playlist_create(user=user_id,
                                                name=name,
                                                public=False,
                                                description=f"100(ish) of the top songs from {date}.")
    playlist_id = new_playlist["id"]
    spotify.playlist_add_items(playlist_id=playlist_id, items=song_list)
    messagebox.showinfo(title="Success", message=f"Your new playlist called {name} is ready!")


# pull top 100 songs from Billboard
def pull_songs():
    date = calendar.get()
    response = requests.get(url=START_URL + date)
    soup = BeautifulSoup(response.text, "html.parser")
    songs_div = soup.find(name="div", class_="chart-results-list")
    chart_divs = songs_div.find_all(name="li", class_="o-chart-results-list__item")
    top_100 = {}
    for item in chart_divs:
        if item.find(name="h3", id="title-of-a-story") and item.find(name="span", class_="c-label"):
            song = item.find(name="h3", id="title-of-a-story").getText().strip("\n")
            artist = item.find(name="span", class_="c-label").getText().strip("\n")
            new_dict = {song: artist}
            top_100.update(new_dict)
    return top_100


# application user interface to make the process friendlier
window = Tk()
window.title("Spotify Time Machine")
window.config(width=1616, height=960)

background = PhotoImage(file="images/spotify-time-machine.gif")

canvas = Canvas(width=1616, height=960)
canvas.create_image(0, 0, anchor="nw", image=background)
canvas.place(x=0, y=0)

calendar = DateEntry(window, selectmode="day", date_pattern="yyyy-mm-dd")
calendar.place(x=105, y=600)
calendar.tk_setPalette(FG)
calendar.configure(background="black", foreground=FG)

date_label = Label(text="Choose day to go back in time:")
date_label.config(fg=FG, bg="black", font=FONT)
date_label.place(x=100, y=560)

info_label = Label(text="Create a Spotify playlist with the top 100 songs \nfrom any date.")
info_label.config(fg=FG, bg="black", font=FONT, anchor="e", justify=LEFT)
info_label.place(x=100, y=400)

button = Button(text="Create Playlist")
button.config(fg=FG, bg="black", width=25, command=search_songs)
button.place(x=220, y=598)

window.mainloop()
