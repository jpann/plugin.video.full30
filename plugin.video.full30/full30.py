import urllib2
from bs4 import BeautifulSoup
from datetime import datetime
import time
import requests

class Full30:
    def __init__(self, url):
        self.opener = urllib2.build_opener()
        self.opener.addheaders = [('User-agent', 'Mozilla/5.0')]

        self.url = url
        self.channels_url = self.url + "/channels/all"
        self.video_url = self.url + "/video/{0}"
        self.api_recent_url = self.url + "/api/v1.0/channel/{0}/recent-videos?page={1}"
        self.thumbnail_url = self.url + "/cdn/videos/{0}/{1}/thumbnails/320x180_{2}.jpg"
        self.mp4_url = "https://videos.full30.com/bitmotive/public/full30/v1.0/videos/{0}/{1}/640x360.mp4"
        self.channel_url = self.url + "/channels/{0}"

    def get_channels(self):
        channels = []

        html = self.opener.open(self.channels_url)
        data = html.read()

        soup = BeautifulSoup(data, "html.parser")

        videostreams = soup.find(class_="video-stream")

        for video in videostreams.find_all('div'):
            channel_slug = url.rsplit('/', 1)[-1]

            channel_metadata = self.get_channel_metadata(channel_slug)

            channel_url = self.url + video.find('a').get('href')
            channel_name = video.find('h4', class_='thumbnail-title').string.encode('ascii', 'ignore').decode('ascii')
            channel_thumbnail = "http:" + video.find('img', class_="thumbnail").get('src')
            channel_image = channel_metadata['image']
            channel_desc = channel_metadata['desc']

            channels.append(
                {
                    "name" : channel_name,
                    "url" : channel_url,
                    "thumbnail" : channel_thumbnail,
                    'image' : channel_image,
                    'desc' : channel_desc
                })

        return channels

    def get_featured(self, url):
        featured = { 'title' : '', 'slug' : '', 'pages' : '', 'videos' : [] }

        channel_slug = url.rsplit('/', 1)[-1]

        html = self.opener.open(url)
        data = html.read()

        soup = BeautifulSoup(data, "html.parser")

        metadata = self.get_channel_metadata_from_data(soup)

        featured['title'] = soup.find('meta', property='og:title').get('content')
        featured['slug'] = channel_slug
        featured['metadata'] = metadata

        featured_videos = soup.find(class_="thumbnail-wrapper featured-thumbnail-wrapper")

        if featured_videos:
            for video in featured_videos.find_all('div', class_="thumbnail-box"):
                video_url = self.url + video.find('a').get('href').encode('ascii', 'ignore').decode('ascii')
                video_name = video.find('h4', class_='thumbnail-title').string.encode('ascii', 'ignore').decode('ascii')
                video_thumbnail = "http:" + video.find('img', class_="thumbnail").get('src')
                video_hash = video_url.rsplit('/', 1)[-1]

                featured['videos'].append(
                    {
                        "title" : video_name,
                        "url" : video_url,
                        "thumbnail" : video_thumbnail,
                        "hash" : video_hash
                    })

        return featured

    def get_recent_by_page(self, url, page):
        recent = { 'title' : '', 'slug' : '', 'pages' : '', 'videos' : [] }

        if not page:
            page = 1

        channel_name = url.rsplit('/', 1)[-1]
        api_url = self.api_recent_url.format(channel_name, page)

        r = requests.get(api_url, headers={'User-Agent' : 'Mozilla/5.0'})

        if not r:
            return None

        data = r.json()

        if not data:
            return None

        recent['title'] = data['channel']['title']
        recent['pages'] = data['pages']
        recent['slug'] = data['channel']['slug']
        recent['metadata'] = self.get_channel_metadata(data['channel']['slug'])

        for video in data['videos']:
            v_hash = video['hashed_identifier']
            v_id = video['id']
            v_thumbnail = self.thumbnail_url.format(recent['slug'], v_hash, video['thumbnail_filename'])
            v_title = video['title']
            v_url = self.video_url.format(v_hash)
            v_channel = recent['title']
            v_mp4_url = self.mp4_url.format(recent['slug'], v_hash)

            recent['videos'].append({ "title" : v_title, "url" : v_url, "thumbnail" : v_thumbnail, "channel": v_channel, "mp4_url" : v_mp4_url, "hash" : v_hash })

        return recent

    def get_video_mp4(self, url):
        video_url = ''

        html = self.opener.open(url)
        data = html.read()

        soup = BeautifulSoup(data, "html.parser")

        video = soup.find('video', id="video-embed")

        if video:
            video_source = video.find('source', type='video/mp4; codecs="avc1.64001E, mp4a.40.2"')

            if video_source:
                video_url = video_source.get('src')

        return video_url

    def get_video_metadata(self, video_hash):
        metadata = {}

        url = self.video_url.format(video_hash)

        html = self.opener.open(url)
        data = html.read()

        soup = BeautifulSoup(data, "html.parser")

        uploaded = soup.find('span', class_="fa fa-calendar").text.replace("Uploaded:", "").strip()
        date = ''

        if uploaded:
            try:
                date = datetime.strptime(uploaded, "%m/%d/%Y")
            except TypeError:
                date = datetime.fromtimestamp(time.mktime(time.strptime(uploaded, "%m/%d/%Y")))

        metadata['desc'] = soup.find('meta', property='og:description').get('content')
        metadata['uploaded'] = date
        metadata['views'] = soup.find('span', id="player-view-count").text

        return metadata

    def get_channel_metadata(self, slug):
        metadata = {}

        url = self.channel_url.format(slug)

        html = self.opener.open(url)
        data = html.read()

        soup = BeautifulSoup(data, "html.parser")

        metadata['url'] = soup.find('meta', property='og:url').get('content')
        metadata['title'] = soup.find('meta', property='og:title').get('content')
        metadata['desc'] = soup.find('meta', property='og:description').get('content')
        metadata['image'] = self.url + soup.find('img', class_='channel-banner').get('src')

        return metadata

    def get_channel_metadata_from_data(self, soup):
        metadata = {}

        metadata['url'] = soup.find('meta', property='og:url').get('content')
        metadata['title'] = soup.find('meta', property='og:title').get('content')
        metadata['desc'] = soup.find('meta', property='og:description').get('content')
        metadata['image'] = self.url + soup.find('img', class_='channel-banner').get('src')

        return metadata
