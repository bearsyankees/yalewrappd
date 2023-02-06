
# YaleWrappd
This is the code powering the site [yalewrappd.com](https://www.yalewrappd.com). This site is used by hundreds of Yale students to get a feel for what the campus was listening to.

## Languages/Libraries/Other Tech Used

Python

Flask

SpotifyAPI

Redis

GoogleAuth

Heroku



## What is it?

YaleWrappd, as the name implies, is a Yale-centric version of Spotify wrappd. It generates a playlist of top songs at Yale and stores data of the top artists, which were released to the public via the Spring Fling Instagram.

## How does it work?

YaleWrappd forces users to sign in with their Yale email, to first verify they go to the institution. It then has them login with Spotify, and saves in a Redis DB their top songs and artists (checks if the user ID already exists in the DB as to not have duplicates). It then shows the user their top 50 artists of the last 6 months and adds a unique song to [this playlist](https://open.spotify.com/playlist/57IF8qCfvZTi06QQHqvYIv?si=f3adf20aa08748cc) of Yale's top songs.

Most of the work is done in spotify/main.py
