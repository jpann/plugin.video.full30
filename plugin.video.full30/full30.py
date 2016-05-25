import urllib2
from bs4 import BeautifulSoup

class Full30:
    def __init__(self, url):
        self.opener = urllib2.build_opener()
        self.opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        
        self.url = url
        self.channels_url = self.url + "/channels/all"
       
    def get_channels(self):
        channels = []

        html = self.opener.open(self.channels_url)
        data = html.read()

        soup = BeautifulSoup(data, "html.parser")

        videostreams = soup.find(class_="video-stream")

        for video in videostreams.find_all('div'):
            channel_url = self.url + video.find('a').get('href')
            channel_name = video.find('h4', class_='thumbnail-title').string.encode('ascii', 'ignore').decode('ascii')
            channel_thumbnail = "http:" + video.find('img', class_="thumbnail").get('src')

            channels.append({ "name" : channel_name, "url" : channel_url, "thumbnail" : channel_thumbnail })

        return channels
        
    def get_featured(self, url):
        featured = []

        html = self.opener.open(url)
        data = html.read()

        soup = BeautifulSoup(data, "html.parser")

        featured_videos = soup.find(class_="thumbnail-wrapper featured-thumbnail-wrapper")
        
        if featured_videos:
            for video in featured_videos.find_all('div', class_="thumbnail-box"):
                video_url = self.url + video.find('a').get('href').encode('ascii', 'ignore').decode('ascii')
                video_name = video.find('h4', class_='thumbnail-title').string.encode('ascii', 'ignore').decode('ascii')
                video_thumbnail = "http:" + video.find('img', class_="thumbnail").get('src')

                featured.append({ "title" : video_name, "url" : video_url, "thumbnail" : video_thumbnail })

        return featured
    
    def get_recent(self, url):
        recent = []

        html = self.opener.open(url)
        data = html.read()

        soup = BeautifulSoup(data, "html.parser")

        recent_videos = soup.find(class_="thumbnail-wrapper recent-thumbnail-wrapper")
        
        if recent_videos:
            for video in recent_videos.find_all('div', class_="thumbnail-box"):
                video_url = self.url + video.find('a').get('href').encode('ascii', 'ignore').decode('ascii')
                video_name = video.find('h4', class_='thumbnail-title').string.encode('ascii', 'ignore').decode('ascii')
                video_thumbnail = "http:" + video.find('img', class_="thumbnail").get('src')

                recent.append({ "title" : video_name, "url" : video_url, "thumbnail" : video_thumbnail })

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