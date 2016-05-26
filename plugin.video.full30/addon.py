import sys
import urllib
from urlparse import parse_qsl
import xbmcgui
import xbmcplugin
from full30 import Full30

_url = sys.argv[0]
_handle = int(sys.argv[1])

xbmcplugin.setContent(_handle, 'movies')

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)
    
url_base = "https://www.full30.com"
full30 = Full30(url_base)

def get_channels():
	listing = []
	
	channels = full30.get_channels()
	
	for channel in channels:
		list_item = xbmcgui.ListItem(channel['name'],  iconImage=channel['thumbnail'])
		
		list_item.setInfo('video', {'title': channel['name']})
		
		url = '{0}?action=list-video-type&channel_url={1}'.format(_url, channel['url'])
		
		is_folder = True
		
		listing.append((url, list_item, is_folder))
		
	xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
	
	xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
	
	xbmcplugin.endOfDirectory(_handle)

def list_video_type(channel_url):
	list_item = xbmcgui.ListItem(label='Featured',  iconImage='DefaultVideo.png')
	url = '{0}?action=listing&type=featured&channel_url={1}'.format(_url, channel_url)
	xbmcplugin.addDirectoryItem(handle=_handle, url=url, listitem=list_item, isFolder=True)
	
	list_item = xbmcgui.ListItem(label='Recent',  iconImage='DefaultVideo.png')
	url = '{0}?action=listing&type=recent&channel_url={1}'.format(_url, channel_url)
	xbmcplugin.addDirectoryItem(handle=_handle, url=url, listitem=list_item, isFolder=True)
	
	xbmcplugin.endOfDirectory(_handle)

def list_videos_featured(channel_url):
	featured_videos = full30.get_featured(channel_url)
	
	listing = []
	
	for video in featured_videos:
		video_url = full30.get_video_mp4(video['url'])
		
		list_item = xbmcgui.ListItem(label=video['title'], iconImage=video['thumbnail'])
		
		list_item.setInfo('video', {'title': video['title'] })
		 
		list_item.setProperty('IsPlayable', 'true')
		 
		url = '{0}?action=play&video={1}'.format(_url, video_url)
		 
		is_folder = False
		 
		listing.append((url, list_item, is_folder))
		 
	xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
	
	xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)

	xbmcplugin.endOfDirectory(_handle)

def list_videos_recent_pages(channel_url, page = 1):		
	featured_videos = full30.get_recent_by_page(channel_url, page)
	
	listing = []
	
	pages = featured_videos['pages']

	for video in featured_videos['videos']:
		video_url = full30.get_video_mp4(video['url'])
		
		list_item = xbmcgui.ListItem(label=video['title'], iconImage=video['thumbnail'])
		
		list_item.setInfo('video', {'title': video['title'] })
		 
		list_item.setProperty('IsPlayable', 'true')
		 
		url = '{0}?action=play&video={1}'.format(_url, video_url)
		 
		is_folder = False
		 
		listing.append((url, list_item, is_folder))
		 
	xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
	
	next_page = int(page) + 1
	if next_page <= pages:
		list_item = xbmcgui.ListItem(label='Page ' + str(next_page) + ' >>',  iconImage='DefaultVideo.png')
		
		url = '{0}?action=listing&type=recent&channel_url={1}&page={2}'.format(_url, channel_url, next_page)
		
		xbmcplugin.addDirectoryItem(handle=_handle, url=url, listitem=list_item, isFolder=True)

	xbmcplugin.endOfDirectory(_handle)
	
def play_video(path):
	play_item = xbmcgui.ListItem(path=path)
	
	xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)
	
def router(paramstring):
	params = dict(parse_qsl(paramstring))
	
	if params:
		if params['action'] == 'listing':
			if params['type'] == 'featured':
				list_videos_featured(params['channel_url'])
			elif params['type'] == 'recent':
				if 'page' in params:
					list_videos_recent_pages(params['channel_url'], params['page'])
				else:
					list_videos_recent_pages(params['channel_url'], 1)
		elif params['action'] == 'list-video-type':
			list_video_type(params['channel_url'])
		elif params['action'] == 'play':
			play_video(params['video'])
	else:
		get_channels()
		
if __name__ == '__main__':
    router(sys.argv[2][1:])