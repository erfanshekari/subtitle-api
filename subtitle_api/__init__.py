import os
import shutil
import zipfile
import asyncio
import requests
from bs4 import BeautifulSoup
from imdb import IMDb

# This Module is a web Crawler that makes requests to subscene.com and parse it for best results


class SubtitleAPI:
    def __init__(self, *args):  # args are languages pass it like ('english', 'persian')
        self.request_header = {
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
        }
        self.url = 'https://www.subscene.com'
        self.search_page_slugs = '/subtitles/searchbytitle'  # subscene search slug
        self.temp_dir = os.path.abspath(os.path.join(os.path.curdir, 'temp'))
        self.excuter_loop = asyncio.get_event_loop()
        if not os.path.isdir(self.temp_dir):
            os.mkdir(self.temp_dir)

        self.langs = []
        if args:
            for lang in args:
                self.langs.append(lang.lower())

    def enable_imdb(self):
        self.imdb = IMDb()

    def imdb_find(self, id):
        instance = self.imdb.get_movie(id)
        title = instance.get('title', None)
        year = instance.get('year', None)
        return (title, year)

    # Method Bellow returns a BeautifulSoup object of our html response
    def parse(self, html):
        return BeautifulSoup(html, 'html.parser')

    # this method simply call and endpoint and return it as plantext
    def get_html(self, url):
        response = requests.get(url).text
        return response

    # this method can make a search query to subscene and a list of dict results contain name and link
    def search(self, title):
        response = requests.post(f'{self.url}{self.search_page_slugs}', data={
                                 'query': title}, headers=self.request_header).text
        return self.remove_duplicate_dicts(self.parse_search_results(self.parse(response)))

    # this method parse html to extract only results and return as list
    def parse_search_results(self, soup):
        results = []
        for element in soup.find(class_="search-result").find_all('li'):
            element = element.find('a')
            link = element.get('href')
            name = element.get_text()
            results.append({'link': link, 'name': name})
        # a list of dicts [...,{...},{'link': '/', 'name': ''},{...},...]
        return results

    def remove_duplicate_dicts(self, ListOfDicts):
        toSet = set()
        newListOFDicts = []
        for i in ListOfDicts:
            y = tuple(i.items())
            if y not in toSet:
                toSet.add(y)
                newListOFDicts.append(i)
        return newListOFDicts

    # this method excutes ascync functions
    def download(self):
        if hasattr(self, 'memory_state'):
            self.excuter_loop.run_until_complete(self.download_queue())
            return self
        return self

    # extract() method will look for all downloaded zip files and extract it , then return subtitle files as list
    def extract(self):
        if hasattr(self, 'memory_state'):
            for index, obj in enumerate(self.memory_state):
                zip_file = obj.get('zip', None)
                if zip_file:
                    items = self.extract_zip(zip_file)
                    self.memory_state[index].update({'items': items})
        return self

    # This method will download zip file and return it as file path
    async def download_zip(self, url, name):
        localFileName = f'{self.temp_dir}/{name}.zip'
        with requests.get(url, stream=True) as r:
            with open(localFileName, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        # absolute path of downloaded file
        return os.path.abspath(localFileName)

    # this method will scrape all download links of memory state
    async def scrape_for_download_queue(self):
        for index, obj in enumerate(self.memory_state):
            link = obj.get('link', None)
            if link:
                try:
                    get_Obj = await self.scrape_download_page(f'{self.url}{link}')
                    if get_Obj:
                        self.memory_state[index].update(get_Obj)
                except:
                    print('probelm while connecting')
                    pass

    # download zip files in queue
    async def download_queue(self):
        await self.scrape_for_download_queue()
        if True:
            for index, obj in enumerate(self.memory_state):
                download = obj.get('download', None)
                if download:
                    try:
                        zip_local_path = {'zip': await self.download_zip(f'{self.url}{download}', obj['name'])}
                        self.memory_state[index].update(zip_local_path)
                    except:
                        pass

    # this method walk to directored passed as argument and return all subtitle files absolute path as list
    def walk_for_subtitle(self, path):
        all_files = []

        def walk_for_all(path):
            for current, dirs, files in os.walk(path):
                if files:
                    for file in files:
                        if '.' in file:
                            splitted_name = file.split('.')
                            if splitted_name[-1] in ['srt', 'sub']:
                                all_files.append(os.path.join(
                                    os.path.abspath(current), file))
                if dirs:
                    for new_dir in dirs:
                        new_path = os.path.join(current, new_dir)
                        return walk_for_all(new_path)
        walk_for_all(path)
        return all_files

    # this method extraxt a zip file and return all subtitles
    def extract_zip(self, zip):
        name = os.path.basename(zip).replace('.', '')
        dir_to_apply = os.path.join(self.temp_dir, name)
        if not os.path.isdir(dir_to_apply):
            os.mkdir(dir_to_apply)
        with zipfile.ZipFile(zip, 'r') as zip_ref:
            zip_ref.extractall(dir_to_apply)
        if True:
            return self.walk_for_subtitle(dir_to_apply)

    # filter_langs(listOfDirectories) method filter initalized langs an returm a new list of subtitles

    def filter_langs(self, listDicts):
        if self.langs:
            newList = []
            for sub in listDicts:
                if sub['lang'].lower() in self.langs:
                    newList.append(sub)
            return newList
        return listDicts

    # this method return subtitle and link for download page

    def scrape_list(self, url):
        soup = self.parse(self.get_html(url))
        items = []
        for element in soup.find_all('td', class_='a1'):
            lang, name = None, None
            link = element.a.get('href')
            for index, child in enumerate(element.a.children):
                if child.name == 'span':
                    spanValue = child.text.strip().lower()
                    if index == 1:
                        lang = spanValue
                    elif index == 3:
                        name = spanValue
                if lang and name and link:
                    items.append({
                        'lang': lang,
                        'name': name,
                        'link': link
                    })
        # return list like: [...,{'lang':'english', 'name':'Movie Name', 'link':'/slug'},...]
        return self.filter_langs(items)

    # scrape_download_page(url) method scrape subtitle author, download link and release information
    async def scrape_download_page(self, url):
        soup = self.parse(self.get_html(url))
        release_info_list = []
        author, download = None, None
        for element in soup.find_all('li', class_='release'):
            for child in element.children:
                if child.name == 'div':
                    release_info_list.append(child.text.strip().lower())
        for element in soup.find_all('li', class_='author'):
            for child in element.children:
                if child.name == 'a':
                    author = child.text.strip()
        download = soup.find(id='downloadButton').get('href')
        if author and download and release_info_list:
            return {
                'author': author,
                'release_info': release_info_list,
                'download': download
            }
        return {}

    # filter_release_type(ListOfDicts, typeOfRelease) method filters based on type of release passed in
    def filter_release_type(self, ListOfDicts, typeOfRelease):
        newListOfDicts = []
        for obj in ListOfDicts:
            name = obj.get('name', None)
            if typeOfRelease in name:
                newListOfDicts.append(obj)
        return newListOfDicts

    # filter based on seasons

    def find_season(self, listOfDicts, title, num):
        seasons = [(1, 'First Season'), (2, 'Second Season'), (3, 'Third Season'), (4, 'Fourth Season'), (5, 'Fifth Season'),
                   (6, 'Sixth Season'), (7, 'Seventh Season'), (8, 'Eighth Season'), (9, 'Ninth Season'), (10, 'Tenth Season'), (11, 'Eleventh Season'), (
                       12, 'Twelfth Season'), (13, 'Thirteenth Season'), (14, 'Fourteenth Season'), (15, 'Fifteenth Season'), (16, 'Sixteenth Season'),
                   (17, 'Seventeenth Season'), (18, 'Eighteenth Season'), (19, 'Nineteenth Season'), (20, 'Twentieth Season')]
        detect_season = None
        for index, season in seasons:
            if index == num:
                detect_season = season
        newListOfDicts = []
        if listOfDicts:
            for obj in listOfDicts:
                name = obj.get('name', None)
                if name:
                    if detect_season in name and title in name:
                        newListOfDicts.append(obj)
            return newListOfDicts
        return []

    # this method make a string like S01E05 for subscene tv series search pattern

    def make_series_target_string(self, se, ep):
        if se < 10:
            se = f'0{se}'
        if ep < 10:
            ep = f'0{ep}'
        return f'S{se}E{ep}'.lower()

    # this method filter subtitles based on episode number

    def filter_episodes(self, ListOfDicts, string):
        newListOfDicts = []
        for obj in ListOfDicts:
            name = obj.get('name', None)
            if name:
                if string in name:
                    newListOfDicts.append(obj)
        return newListOfDicts

    # this method returns subtitles as list of dicts filterd and ready to download
    def movie(self, title=None, year=None, imdb_id=None, release_type=None):
        if imdb_id:
            if not hasattr(self, 'imdb'):
                self.enable_imdb()
            title, year = self.imdb_find(imdb_id)

        search_results = self.search(title)
        if len(search_results) > 1:
            filtered_results = []
            for obj in search_results:
                name = obj.get('name', None)
                if year:
                    if str(year) in name:
                        filtered_results.append(obj)
                else:
                    filtered_results = search_results
            search_results = filtered_results

        if search_results:
            link = search_results[0]['link']
            url = f'{self.url}{link}'
            sub_list = self.scrape_list(url)
            if release_type:
                sub_list = self.filter_release_type(sub_list, release_type)
            self.memory_state = sub_list
        return self

    # tvshow method returns list of subtitles target based on filter passed in
    def tvshow(self, title=None, imdb_id=None, release_type=None, season=None, episode=None):
        if imdb_id:
            if not hasattr(self, 'imdb'):
                self.enable_imdb()
            title, _ = self.imdb_find(imdb_id)

        search_results = self.search(title)
        if season:
            search_results = self.find_season(search_results, title, season)
        if search_results:
            link = search_results[0]['link']
            url = f'{self.url}{link}'
            sub_list = self.scrape_list(url)
            if release_type:
                sub_list = self.filter_release_type(sub_list, release_type)

            if season and episode:
                se = self.make_series_target_string(season, episode)
                sub_list = self.filter_episodes(sub_list, se)
            self.memory_state = sub_list
        return self

    def __str__(self):
        str_ = ''
        for string in self.langs:
            str_ += f',{string} '
        return f'<subsceneScraper Class {str_}>'

    # this property return main subtitle state with all dict and keys
    @property
    def subtitles(self):
        if hasattr(self, 'memory_state'):
            return self.memory_state
        return []

    # this method return all downloaded zip files
    @property
    def zip_files(self):
        zip_files = []
        if hasattr(self, 'memory_state'):
            for obj in self.memory_state:
                zip_file = obj.get('zip', None)
                if zip_file:
                    zip_files.append(zip_file)
        return zip_files

    # this method return all extracted subtitle files in memory
    @property
    def all_subtitle_files(self):
        subtitle_files = []
        if hasattr(self, 'memory_state'):
            for obj in self.memory_state:
                items = obj.get('items', None)
                if items:
                    for item in items:
                        subtitle_files.append(item)
        return subtitle_files
