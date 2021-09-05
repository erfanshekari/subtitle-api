# Browse and Download from subscene.com with just a few lines of python code !

SubtitleAPI is a python package that provide direct access to subtitle content using scraping techniques! You can search for any subtitle you want , also add query filters to your search to remove unwanted content!
## Intsall SubtitleAPI using pip
```
pip install SubtitleAPI
```
Get Movie Subtitles:
```
from subtitleAPI import SubtitleAPI

subscene = SubtitleAPI('english','farsi/persian') # pass languages you want to have in results

subtitle.movie(title='Tenet',year=2020,release_type='bluray')
subtitle.download()
```
# search IMdB ID
```
subtitle.movie(imdb_id='6723592',release_type='bluray')
```
# search for TV Shows

```

subtitle.tvshow(title='Game of Thrones',release_type='bluray',season=2,episode=3)

# or

subtitle.tvshow(imdb_id='0944947',release_type='bluray',season=2,episode=3)

```
