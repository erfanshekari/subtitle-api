# Browse and Download from subscene.com with just a few lines of python

SubtitleAPI is a python package provide direct access to subscene.com content using scraping techniques! You can search for any subtitle you want to download , also add query filters to remove unwanted content!
## Intsall SubtitleAPI using pip
```shell
pip install subtitle-api
```
Get Movie Subtitles:
```py
from subtitle_api import SubtitleAPI

subscene = SubtitleAPI('english','farsi/persian') # pass languages you want to have in results

subscene.movie(title='Tenet',year=2020,release_type='bluray')
subscene.download()
```
# Search IMdB ID
```py
subscene.movie(imdb_id='6723592',release_type='bluray')
```
# Search For TV Shows

```py

subscene.tvshow(title='Game of Thrones',release_type='bluray',season=2,episode=3)

# or

subscene.tvshow(imdb_id='0944947',release_type='bluray',season=2,episode=3)

```
# Export zip files After download is Finished !
this method extract all zip files.
```py
subscene.download().extract()

```
# Some Useful Properties:
```py
subscene.subtitles # all subtitle objects in memory
subscene.zip_files # downloaded zip files!
subscene.all_subtitle_files # all extracted subtitle files
```
