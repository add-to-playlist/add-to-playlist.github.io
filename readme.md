# Add to Playlist

An independent catalogue of every track chosen on [Add to Playlist](https://www.bbc.co.uk/programmes/m00106lb), the BBC Radio 4 show in which the presenters and their guests build a playlist each episode, every track linked to the one before it.

BBC Sounds lists each episode's tracks individually, but never as one list. This repo holds the data and the static site generator that compiles it into one: https://add-to-playlist.github.io/

Python and Jinja2 render the JSON in `src/data/` into a static site, which GitHub Actions builds and deploys to Pages on every push to `main`.

## A note on data

Most of the data was gathered automatically by scraping each episode's BBC Sounds page and querying Spotify's Web API for a recording. Because of how that search behaves, there may be slight inconsistencies between the Spotify link and the version played on the show (a remix appearing ahead of the original, for instance). Shazam and SoundHound were used to identify the exact recordings where possible.

Episode runtimes are measured from the audio with `ffprobe`. One episode's published duration claims 60 seconds, and many share identical values that don't match their actual runtimes.

Although care has been taken, there will probably be a few mistakes; corrections are therefore very much welcomed!

> [!IMPORTANT]
> **Disclaimer**
>
> This project is an independent compilation and analysis of Add to Playlist episodes. It is not affiliated with or endorsed by the BBC.
