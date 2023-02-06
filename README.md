
# YaleWrappd
This is the code powering the site [yalewrappd.com](https://www.yalewrappd.com). This site is used by hundreds of Yale students to get a feel for what the campus is listening to.

## Languages/Libraries/Other Tech Used

Python

Flask

SpotifyAPI

Redis

GoogleAuth

Heroku



## What is it?

YaleWrappd, as the name implies, is a Yale-centric version of Spotify wrappd. It generates a playlist of top songs listened to by Yale students, by using the Spotify API to see users top songs. It also stores data on the most-popular artists.  The auto-generated playlist is shared with the user, and the top artist data is then released to the Yale commumnity via the “Spring Fling” Instagram. [Spring Fling is the annual large concert put on by Yale. Typically very popular music stars are booked for the event.]

## How does it work?

YaleWrappd process flow:

* Users first sign in with their Yale credentials, to verify that they are affiliated with the university.
* YaleWrappd then directs them to login to their Spotify account, reads their data and saves in a Redis DB their top songs and artists. It also checks if the user ID already exists in the DB as to not have duplicate entries and skew the data.
* YaleWrappd then shows the user their top 50 artists of the last 6 months and adds a unique song to [this playlist](https://open.spotify.com/playlist/57IF8qCfvZTi06QQHqvYIv?si=f3adf20aa08748cc) of Yale's top songs.


Most of the work is done in spotify/main.py
