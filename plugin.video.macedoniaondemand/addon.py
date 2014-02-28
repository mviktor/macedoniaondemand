# -*- coding: utf-8 -*- 

"""
	Macedonia On Demand XBMC addon.
	Watch videos and live streams from Macedonian TV stations, and listen to live radio streams.
	Author: Viktor Mladenovski
"""

import urllib,urllib2,re,xbmcplugin,xbmcaddon,xbmcgui,HTMLParser
import sys,os,os.path
from BeautifulSoup import BeautifulSoup

user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:11.0) Gecko/20100101 Firefox/11.0'
str_accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'

ADDON=__settings__ = xbmcaddon.Addon(id='plugin.video.macedoniaondemand')
DIR_USERDATA = xbmc.translatePath(ADDON.getAddonInfo('profile'))
VERSION_FILE = DIR_USERDATA+'version.txt'
VISITOR_FILE = DIR_USERDATA+'visitor.txt'

__version__ = ADDON.getAddonInfo("version")

if not os.path.isdir(DIR_USERDATA):
	os.makedirs(DIR_USERDATA)

def platformdef():
	if xbmc.getCondVisibility('system.platform.osx'):
		if xbmc.getCondVisibility('system.platform.atv2'):
			log_path = '/var/mobile/Library/Preferences'
			log = os.path.join(log_path, 'xbmc.log')
			logfile = open(log, 'r').read()
		else:
			log_path = os.path.join(os.path.expanduser('~'), 'Library/Logs')
			log = os.path.join(log_path, 'xbmc.log')
			logfile = open(log, 'r').read()
	elif xbmc.getCondVisibility('system.platform.ios'):
		log_path = '/var/mobile/Library/Preferences'
		log = os.path.join(log_path, 'xbmc.log')
		logfile = open(log, 'r').read()
	elif xbmc.getCondVisibility('system.platform.windows'):
		log_path = xbmc.translatePath('special://home')
		log = os.path.join(log_path, 'xbmc.log')
		logfile = open(log, 'r').read()
	elif xbmc.getCondVisibility('system.platform.linux'):
		log_path = xbmc.translatePath('special://home/temp')
		log = os.path.join(log_path, 'xbmc.log')
		logfile = open(log, 'r').read()
	else:
		logfile='Starting XBMC (Unknown Git:.+?Platform: Unknown. Built.+?'

	match=re.compile('Starting XBMC \((.+?) Git:.+?Platform: (.+?)\. Built.+?').findall(logfile)
	for build, platform in match:
		if re.search('12.0',build,re.IGNORECASE):
			build="Frodo"
		if re.search('11.0',build,re.IGNORECASE):
			build="Eden"
		if re.search('13.0',build,re.IGNORECASE):
			build="Gotham"
		return platform

	return "Unknown"

def fread(filename):
	ver = ''
	h = open(filename, "r")
	try:
		data = h.read()
	finally:
		h.close()
	return data

def fwrite(filename, data):
	h = open(filename, "wb")
	try:
		h.write(data)
	finally:
		h.close()

def get_visitorid():
	if os.path.isfile(VISITOR_FILE):
		visitor_id = fread(VISITOR_FILE)
	else:
		from random import randint
		visitor_id = str(randint(0, 0x7fffffff))
		fwrite(VISITOR_FILE, visitor_id)

	return visitor_id

__visitor__ = get_visitorid()

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):

                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]

        return param

def setView(content='movies', mode=503):
	return 0
#	xbmcplugin.setContent(int(sys.argv[1]), content)
#	xbmc.executebuiltin("Container.SetViewMode("+str(mode)+")")


# ZULU live 

def createZuluListing():
	url='http://on.net.mk/zulu'
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	match=re.compile('<span class="field-content"><a href="/zulu/(.+?)"><img .+? src="(.+?)" /></a></span>').findall(link)
	#for station, thumb in match:
	#	print station, thumb
	return match

def playZuluStream(url):
	pDialog = xbmcgui.DialogProgress()
	pDialog.create('Zulu Stream', 'Initializing')
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	pDialog.update(50, 'Fetching video stream')
	response = urllib2.urlopen(req)
	link = response.read()
	response.close()

	#streammatch = re.compile('<a class="playButton" href="(.+?)">').findall(link)
	streammatch = re.compile('<video .+? src="(.+?)"').findall(link)
	titlematch = re.compile('class="title">(.+?)</h1>').findall(link)
	playurl(streammatch[0])
	pDialog.update(80, 'Playing')

	return True

# TELEKABEL live

def createTelekabelListing():
	url='http://telekabel.com.mk/index.php/mk/%D1%81%D1%82%D1%80%D0%B8%D0%BC%D0%B8%D0%BD%D0%B3?view=featured'

	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	req.add_header('Accept', str_accept)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	match=re.compile('<li class="level2 item.+?"><a href=\"(.+?)\" class="level2"><span>(.+?)</span></a></li>').findall(link)
	return match


def playTelekabelStream(url):
	pDialog = xbmcgui.DialogProgress()
	pDialog.create('Telekabel Stream', 'Initializing')
	req = urllib2.Request('http://telekabel.com.mk'+url)
	req.add_header('User-Agent', user_agent)
	req.add_header('Accept', str_accept)
	pDialog.update(30, 'Fetching video stream 30%')
	response = urllib2.urlopen(req)
	link = response.read()
	response.close()

	nextframematch = re.compile('name="iframe"\n\t\tsrc="(.+?)"').findall(link)

	req = urllib2.Request('http://telekabel.com.mk'+nextframematch[0])
	req.add_header('User-Agent', user_agent)
	req.add_header('Accept', str_accept)
	pDialog.update(60, 'Fetching video stream 60%')
	response = urllib2.urlopen(req)
	link = response.read()
	streammatch = re.compile("file:'(.+?)'").findall(link)

	pDialog.update(80, 'Playing')
	playurl(streammatch[0])
	pDialog.close()

	return True



# ON NET methods

def createOnnetRadioListing():
	url='http://on.net.mk/radio'
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	match=re.compile('\t<li id="(.+?)">\n\t<a class="main-link" rel="(.+?)">(.+?)</a>\n\t<a class="external" href="(.+?)"></a>\n\t</li>\n').findall(link)

	#for id, stream,descr,mp3stream in match:
	#	print descr+' '+stream
	return match

# OFF NET methods

def createOffnetRadioListing():
	url='http://off.net.mk/radio'
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	match=re.compile('<a class=".+?" data-id=".+?" data-stream="(.+?)" data-frequency="(.*?)">(.+?)</a>').findall(link[link.find('block-views-live-stream-block'):])
	#for stream,freq,name in match:
	#	print freq+" "+name+" "+stream
	return match

# 24 Vesti methods

def play24VestiVesti():
	pDialog = xbmcgui.DialogProgress()
	pDialog.create('24 Vesti', 'Initializing')
	url='http://24vesti.mk/video/vesti'
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	pDialog.update(50, 'Finding stream')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	match=re.compile('file: "(.+?)"').findall(link)

	pDialog.update(80, 'Playing')
	playurl('http://24vesti.com.mk'+match[0]+'|Cookie=macedoniaondemand')
	pDialog.close()
	return True

def create24VestiEmisiiListing(urlpagenr):
	if urlpagenr == None or urlpagenr == '':
		url = 'http://24vesti.mk/video/emisii'
	else:
		url = 'http://24vesti.mk/video/emisii?page='+urlpagenr


	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	match=re.compile('<div class="views-field views-field-field-teaser-image-fid">.+?<a href="(.+?)" .+?><img src="(.+?)" .+?  \n  .+?  \n  .+?<a href=".+?">(.+?)</a>.+?').findall(link)

	#for u,thumb,title in match:
	#	print title

	return match

def create24VestiVideoSodrzina():
	url='http://24vesti.mk/'

	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()

	match=re.compile('<span class="field-content"><div class="text-wrap">\n   <div class="views-field-title"><a href="(.+?)" class="imagecache imagecache-teaser-medium-wide imagecache-linked imagecache-teaser-medium-wide_linked"><img src="(.+?)" .+?\n   <div class="video-flag">(.+?)</div>\n   <div class="views-field-title"><a href=".+?">(.+?)</a></div>\n</div></span>  </div></li>\n').findall(link)

	#for u,thumb,title1,title2 in match:
	#	print title2.strip()
	return match


def play24VestiVideo(url):
	pDialog = xbmcgui.DialogProgress()
	pDialog.create('24Vesti Video', 'Initializing')
	req = urllib2.Request('http://24vesti.com.mk/'+str(url))
	req.add_header('User-Agent', user_agent)
	pDialog.update(30, 'Fetching video stream')
	response = urllib2.urlopen(req)
	link = response.read()
	response.close()

	filematch = re.compile('<param name="movie" value="(.+?)"').findall(link)
	titlematch = re.compile('<title>(.+?)</title>').findall(link)

	if filematch[0].__contains__('dailymotion'):
		stream = 'plugin://plugin.video.dailymotion_com/?url='+filematch[0].split('/')[-1]+'&mode=playVideo'
	elif filematch[0].__contains__('youtube'):
		stream = 'plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid='+filematch[0].split('/')[-1]
	else:
		stream = filematch[0]

	pDialog.update(60, 'Playing')
	playurl(stream)
	pDialog.close()

	return True


# NOVATV methods

def createNovatvListing(page):
	url = 'http://novatv.mk/index.php?navig=8&cat='

	if page == 'novatv_makedonija':
		url += '2'
	elif page == 'novatv_evrozum':
		url += '9'
	elif page == 'novatv_sekulovska':
		url += '8'
	elif page == 'novatv_dokument':
		url += '14'
	elif page == 'novatv_studio':
		url += '16'
	elif page == 'novatv_aktuel':
		url += '18'
	elif page == 'novatv_globus':
		url += '17'
	elif page == 'novatv_kultura':
		url += '4'
	elif page == 'novatv_zanimlivosti':
		url += '1'

	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	link = response.read()
	response.close()
	match=re.compile('<a class="ostanati_wrap" href="(.+?)"> \t  \t\r\n \t  .+? \r\n \t  <img src="(.+?)"  .+?  />\r\n \t  <h2 style="color:black;">(.+?)</h2>\r\n \t  <p>(.+?)</p>\r\n \t.+?<div class="more" style=".+?">.+?</div> \r\n \t  <div class=".+?" style=".+?">(.+?)</div> </div>\r\n \t  </div>\r\n \t  </a>').findall(link)
	return match


def playNovatvVideo(url):
	pDialog = xbmcgui.DialogProgress()
	pDialog.create('Nova Tv Video', 'Initializing')
	req = urllib2.Request('http://novatv.mk/'+str(url))
	req.add_header('User-Agent', user_agent)
	pDialog.update(30, 'Fetching video stream')
	response = urllib2.urlopen(req)
	link = response.read()
	response.close()

	playlist=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	playlist.clear()
	player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)

	filematch = re.compile('<iframe style=".+?" title="YouTube video player" class="youtube-player" type="text/html" \r\n\r\nwidth=".+?" height=".+?" src="(.+?)" frameborder="0" allowfullscreen></iframe>').findall(link)
	if filematch != []:
		titlematch = re.compile('<h2 class="news_title" >(.+?)</h2>').findall(link)
		listitem = xbmcgui.ListItem(titlematch[0]);

		if filematch[0].__contains__('dailymotion'):
			playlist.add('plugin://plugin.video.dailymotion_com/?url='+filematch[0].split('/')[-1]+'&mode=playVideo', listitem)
		elif filematch[0].__contains__('youtube'):
			playlist.add('plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid='+filematch[0].split('?')[0].split('/')[-1], listitem)
		else:
			playlist.add(filematch[0], listitem)

	filematch = re.compile('<iframe width=".+?" height=".+?" src="(.+?)" frameborder=".+?" allowfullscreen></iframe>').findall(link)
	if filematch != []:
		titlematch = re.compile('<h2 class="news_title" >(.+?)</h2>').findall(link)
		listitem = xbmcgui.ListItem(titlematch[0]);

		oldurl=''
		for u in filematch:
			if u.__contains__('youtube') and u != oldurl:
				listitem = xbmcgui.ListItem('video')
				#listitem.setProperty("PlayPaty", u)
				playlist.add('plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid='+u.split('/')[-1], listitem)
				oldurl=u

	if playlist.size() != 0:
		pDialog.update(60, 'Playing')
		player.play(playlist)
		pDialog.close()

	return True


# RADIOMK methods

def createRadiomkListing():
	url = 'http://www.radiomk.com/live/'
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	link = response.read()
	response.close()
	match = re.compile('<li><a href="(.+?)" rel="dofollow" ><img src="(.+?)" alt=".+?">(.+?)</a></li>').findall(link)
	return match

def playRadiomkstream(url):
	pDialog = xbmcgui.DialogProgress()
	pDialog.create('Radiomk Stream', 'Initializing')

	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	pDialog.update(30, 'Fetching radio stream')
	response = urllib2.urlopen(req)
	link = response.read()
	response.close()
	titlematch = re.compile('<title>(.+?)</title>').findall(link)
	streammatch = re.compile("var stream = '(.+?)'").findall(link)
	if streammatch == []:
		streammatch = re.compile('file=(.+?);').findall(link)
		if streammatch == []:
			streammatch = re.compile('<embed src="(.+?)"').findall(link)

	pDialog.update(60, 'Playing')
	playurl(streammatch[0])
	pDialog.close()

	return True

# TV SITEL methods

def createSitelVideoListing():
	url='http://sitel.com.mk/video'
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	match=re.compile('href="(.+?)" class="video-priloog clearfix">\n<div class="teaser-image"><div class="icon"></div><img src="(.+?)" width=".+?" height=".+?" alt="" /></div>\n<div class="category">.+?</div>\n<h3 class="title">(.+?)</h3>').findall(link)
	return match

def playSitelVideo(url):
	pDialog = xbmcgui.DialogProgress()
	pDialog.create('Sitel Video', 'Initializing')
	req = urllib2.Request("http://sitel.com.mk"+str(url))
	req.add_header('User-Agent', user_agent)
	pDialog.update(50, 'Fetching video stream')
	response = urllib2.urlopen(req)
	link = response.read()
	response.close()

	filematch = re.compile('file: "(.+?)"').findall(link)
	titlematch = re.compile('<title>(.+?)</title>').findall(link)

	if filematch[0].__contains__('rtmp'):
		rtmpurl = filematch[0]
		app=rtmpurl.split('/')[3]+'/'
		apos=rtmpurl.find(app)
		y=rtmpurl[apos+len(app):]
		stream = rtmpurl[:apos+len(app)]+' app='+app+' pageUrl=http://sitel.com.mk swfUrl=http://sitel.com.mk/sites/all/libraries/jw.player/jwplayer.flash.swf playpath='+y+' swfVfy=true'
	else:
		stream = filematch[0]
	pDialog.update(90, 'Playing')
	playurl(stream)
	pDialog.close()

	return True

def playSitelDnevnik():
	playurl('rtmp://video.sitel.com.mk/vod/ app=vod/ pageUrl=http://sitel.com.mk swfUrl=http://sitel.com.mk/sites/all/libraries/jw.player/jwplayer.flash.swf playpath=mp4:default/files/dnevnik/dnevnik/dnevnik.mp4 swfVfy=true')
	return True

#  MTV methods

def createmrtfrontList():
	url = 'http://play.mrt.com.mk/'
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	match=re.compile('<li class="">\n        <a href="(.+?)">\n            (.+?)        </a>\t\n    </li>').findall(link)
	return match

def duration_in_minutes(duration):
	split_duration=duration.split(':')
	minutes=0
	for i in range(0, len(split_duration)-1):
		minutes = minutes*60 + int(split_duration[i])
	return minutes

def list_mrtchannel(url):
	url = 'http://play.mrt.com.mk'+url
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	list=[]
	match=re.compile('<div class="col-xs-6 col-sm-3 (.+?) content">\n.+?<a href="(.+?)".+?\n.+?<img src="(.+?)".+?\n.+?\n.+?<span class="title gradient">(.+?)</span>').findall(link)

	# extract channels
	for type,url,thumb,title in match:
		list.append([type,url,thumb,'',title])

	match=re.compile('<div class="col-xs-6 col-sm-3 (.+?) content">\n.+?<a href="(.+?)".+?\n.+?<img src="(.+?)".+?\n.+?\n.+?<span class="duration">(.+?)</span>\n.+?<span class="title gradient">(.+?)</span>').findall(link)

	# extract latest videos on current channel
	for type,url,thumb,duration,title in match:
		list.append([type,url,thumb,str(duration_in_minutes(duration)),title])

	return list

def list_mrtlive():
	url = 'http://play.mrt.com.mk/'
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	match=re.compile('<a class="channel" href="(.+?)" data-id=".+?" title="(.+?)">\n.*?<img src="(.+?)"').findall(link[0:link.find('</ul>')])
	return match

def playmrtvideo(url):
	pDialog = xbmcgui.DialogProgress()
	pDialog.create('MRT Play live stream', 'Initializing')
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	pDialog.update(50, 'Fetching video stream')
	response = urllib2.urlopen(req)
	link = response.read()
	response.close()

	match2=re.compile('"playlist":\[{"url":"(.+?)"').findall(link)
	match1 = re.compile('"baseUrl":"(.+?)"').findall(link)

	title = re.compile('<meta property="og:title" content="(.+?)"').findall(link)

	if match2 != [] and match1 != []:
		stream=match1[0]+"/"+match2[0]
		stream=stream[:stream.rfind('/')]+'/master.m3u8'
		if title != []:
			videotitle = title[0]
		else:
			videotitle = 'MRT Video'
		pDialog.update(70, 'Playing')
		playurl(stream)
		pDialog.close()

	return True

#  OTHER live streams methods

def createOtherListing():
	list=[]
	list.append(['Al Jazeera Balkans', 'rtmp://aljazeeraflashlivefs.fplive.net/aljazeeraflashlive-live app=aljazeeraflashlive-live swfUrl=http://www.nettelevizor.com/playeri/player.swf pageUrl=http://ex-yu-tv-streaming.blogspot.se playpath=aljazeera_balkans_high live=true swfVfy=true', 'http://balkans.aljazeera.net/profiles/custom/themes/aljazeera_balkans/images/banner.png'])
	return list

# ALSAT-M methods

def createAlsatRrugaListing():
	url='http://alsat-m.tv/feed/emisione/rruga-drejt/index.1.rss'
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	match=re.compile('<item>\n.+?<title>(.+?)</title>\n.+?<link>(.+?)</link>\n.+?\n.+?\n.+?<enclosure type="image/jpeg" url="(.+?)"').findall(link)
	return match

def createAlsat15mindebatListing():
	url = 'http://alsat-m.tv/emisione/15_min_debat/index.1.html'
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	link = response.read()
	response.close()
	match=re.compile('<div class="video_short">\n        \n                \n            \n        <div class="image_play">\n            <a id=".+?" href=".+?>\n                \n                    <img src="(.+?)" alt=".+?" />\n                    \n                \n            </a>\n        </div>\n        <h4><a href="(.+?)">(.+?)</a></h4>').findall(link[link.find('<div id="videos_latest">'):link.find('<div id="videos_most_popular">')])

	return match

def createAlsat15mindebatLatest():
	url = 'http://alsat.mk/index.php/emisii/index.1.html'
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	link = response.read()
	response.close()
	match=re.compile('<div class="video_short">\n        \n                \n            \n        <div class="image_play">\n            <a id=".+?" href=".+?>\n                \n                    <img src="(.+?)" alt=".+?" />\n                    \n                \n            </a>\n        </div>\n        <h4><a href="(.+?)">(.+?)</a></h4>').findall(link[link.find('<div id="videos_latest">'):link.find('<div id="videos_most_popular">')])

	return match

def playAlsatVideo(url):
	pDialog = xbmcgui.DialogProgress()
	pDialog.create('Alsat Video', 'Initializing')
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	pDialog.update(50, 'Fetching video stream')
	response = urllib2.urlopen(req)
	link = response.read()
	response.close()

	filematch = re.compile('file:"(.+?)"').findall(link)
	titlematch = re.compile('<title>(.+?)</title>').findall(link)

	if filematch[0].__contains__('youtu.be'):
		stream = 'plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid='+filematch[0].split('/')[-1].strip()
	else:
		stream = filematch[0]
	pDialog.update(90, 'Playing')
	playurl(stream)
	pDialog.close()

	return True

# HRT Methods

def createHRTSeriesListing():
	url='http://www.hrt.hr/enz'
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	match=re.compile('<li><a href="(.+?)">(.+?)</a></li>\n                                    \n').findall(link)
	return match

def listHRTEpisodes(url):
	list=[]
	url = url.replace('&amp;', '&')
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)

	try:
		response = urllib2.urlopen(req)
		link = response.read()
		response.close()
	except:
		return list

	match=re.compile('<option selected="selected" value="(.+?)">(.+?)<').findall(link)
	for value,title in match:
		list.append([title.strip(), url+value])

	match=re.compile('option value="(.+?)">(.+?)<').findall(link)
	for value,title in match:
		list.append([title.strip(), url+value])

	return list

def playHRTVideo(url):
	pDialog = xbmcgui.DialogProgress()
	pDialog.create('HRT Video', 'Initializing')
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	pDialog.update(50, 'Fetching video stream')
	response = urllib2.urlopen(req)
	link = response.read()
	response.close()

	filematch = re.compile('<video data-url="(.+?)"').findall(link)
	titlematch = re.compile('<title>(.+?)</title>').findall(link)

	if filematch[0].__contains__('youtu.be'):
		url = 'plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid='+filematch[0].split('/')[-1].strip()
	else:
		url = filematch[0]
	pDialog.update(90, 'Playing')
	playurl(url)
	pDialog.close()

	return True



# Kanal5 Methods

def createKanal5Series():
	url = 'http://www.kanal5.com.mk/vozivo.asp'
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	match=re.compile('<div style="width:150px; height:100px; background-image:url\((.+?)\); background-repeat:no-repeat; background-position: center center; background-size:cover; overflow:hidden;"></div>\r\n                    </a>\r\n                  </div>\r\n                  <h2 style="font-size:17px !important;"><a href="(.+?)" data-rel="prettyPhoto\[iframe\]">(.+?)</a></h2>').findall(link)

	return match

def listKanal5Episodes(url):
	url = url.replace('&amp;', '&')
	req = urllib2.Request('http://www.kanal5.com.mk/'+url)
	req.add_header('User-Agent', user_agent)

	try:
		response = urllib2.urlopen(req)
		link = response.read()
		response.close()
	except:
		return

	match = re.compile('<a href="(.+?)"><div id="video" .+? class="title_tx">(.+?)</div></a>').findall(link)
	return match

def playKanal5Video(url, name):
	pDialog = xbmcgui.DialogProgress()
	pDialog.create('Kanal5', 'Initializing')
	url = url.replace('&amp;', '&')
	req = urllib2.Request('http://www.kanal5.com.mk/'+url)
	req.add_header('User-Agent', user_agent)
	pDialog.update(50, 'Finding stream')
	response = urllib2.urlopen(req)
	link = response.read()
	response.close()
	match = re.compile('file: "(.+?)",').findall(link)

	pDialog.update(80, 'Playing')
	playurl(match[1]+'|Cookie=macedoniaondemand')
	pDialog.close()
	return True

# serbiaplus methods

def listSerbiaPlusCategories():
	url='http://www.serbiaplus.com/'
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	match=re.compile('<li class="cat-item .+?"><a href="(.+?)" title=".+?">(.+?)</a>').findall(link)

	return match

def listSerbiaPlusTVs(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	match=re.compile('<div class="moviefilm">\n.*?<a href="(.+?)">\n.*?<img src="(.+?)" alt="(.+?)".*?\n').findall(link)

	return match

def playSerbiaPlusStream(url):
	pDialog = xbmcgui.DialogProgress()
	pDialog.create('Serbia Plus', 'Initializing')

	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	pDialog.update(50, 'Finding stream')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()

	stream=findSerbiaPlusStream(link)

	if stream != '':
		pDialog.update(80, 'Playing')
		playurl(stream)
		return True
	else:
		pDialog.close()
		return False

def serbiaplussearchurl(intext):
	if intext.find("file:") != -1:
		stream=re.compile('file: "(.+?)"').findall(intext)
	elif intext.find("application/x-vlc-plugin") != -1:
		stream=re.compile('target="(.+?)"').findall(intext)
	elif intext.find("flashvars=") != -1:
		tmp=re.compile('flashvars="src=(.+?)"').findall(intext)
		if tmp != []:
			stream=[urllib.unquote_plus(tmp[0])]
			stream[0]=stream[0].split(' ')[0]
			stream[0]=stream[0].split('&')[0]
	else:
		stream=[]

	if stream != []:
		return stream[0]
	else:
		return ''

def findSerbiaPlusStream(htmltext):
	start = -1
	end = -1
	start=htmltext.find("filmicerik")

	if start == -1:
		return ''

	searcharea = htmltext[start:start+end]
	searcharea = htmltext[start:]

	if searcharea.find("document.write('\\x")!=-1:
		start = searcharea.find("document.write('\\x")
		end = searcharea[start:].find("')")
		encframe = searcharea[start+16:start+end]
		decframe = encframe.decode("string-escape")
		stream = serbiaplussearchurl(decframe)
	else:
		stream = serbiaplussearchurl(searcharea)

	return stream

# general methods

def registerVersion(ver):
	result = True
	url = 'http://macedoniaondemand.com/register_plugin.php?ver='+ver+'&platform='+urllib.quote(platformdef())
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	try:
		response = urllib2.urlopen(req)
		link = response.read()
		response.close()
	except:
		result = False
	return result

def sendto_ga(page,url='',name=''):
	try:
		if page == None or page == '':
			page = 'Home Page'

		ga_link = 'http://www.google-analytics.com/collect?payload_data&v=1&tid=UA-40698392-3&cid='+__visitor__+'&t=appview&an=Macedonia%20On%20Demand&av='+__version__+'&cd='

		if page != None and page != '':
			ga_link += urllib.quote(page)

		if name != None and name != '':
			ga_link += '('+urllib.quote(name)+')'

		if url != None and url != '':
			ga_link += '('+urllib.quote(url)+')'

		req = urllib2.Request(ga_link)
		req.add_header('User-Agent', user_agent)
		response = urllib2.urlopen(req)
		link=response.read()
		response.close()
	except:
		return True

def playurl(url):
	if name == '':
		guititle = 'Video'
	else:
		guititle = name

	if url[:4] == 'rtmp':
		url = url + ' timeout=10'

	listitem = xbmcgui.ListItem(guititle)
	play=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	play.clear()
	play.add(url, listitem)
	player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
	player.play(play)
	return True

def readurl(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link



def PROCESS_PAGE(page,url='',name=''):

	sendto_ga(page,url,name)

	if page == None:
		addDir('Телевизија', 'tv_front', '', '')
		addDir('Радио', 'liveradio_front', '', '')
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == "radio_front":
		addDir("Слушај во живо", "liveradio_front", '', '', '')
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == "liveradio_front":
		addDir('on.net.mk', 'liveradio_onnet', '', '')
		addDir('radiomk.com', 'liveradio_radiomk', '', '')
		addDir('off.net.mk', 'liveradio_offnet', '', '')
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == "liveradio_onnet":
		listing = createOnnetRadioListing()
		counter=0
		for radioid,rtmstream,descr,mp3stream in listing:
			if counter > 14:
				addLink(descr, 'rtmp://217.16.82.2/radio app=radio pageUrl=http://on.net.mk swfUrl=http://on.net.mk/radio/player/player.swf live=true playpath='+rtmstream+' timeout=3 swfVfy=true', '', '')
			counter=counter+1
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == "liveradio_radiomk":
		listing = createRadiomkListing()
		for link, thumb, title in listing:
			addLink(title, link, 'radiomk_playstream', 'http://www.radiomk.com/live/'+thumb)
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == "radiomk_playstream":
		playRadiomkstream(url)

	elif page == "liveradio_offnet":
		listing = createOffnetRadioListing()
		for stream, freq, title in listing:
			addLink((freq+" "+title).strip(), 'rtmp://off.net.mk/radio app=radio pageUrl=http://off.net.mk swfUrl=http://off.net.mk/sites/all/libraries/jwplayer/player.swf live=true playpath='+stream+' timeout=3 swfVfy=true', '', '')
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))


	elif page == "tv_front":
		stations = []
		stations.append(["24 Вести", "24vesti_front", ''])
		stations.append(["НОВА ТВ", "novatv_front", ''])
		stations.append(["Сител", "sitel_front", ''])
		stations.append(["МРТ Play", "mrt_front", ''])
		stations.append(["AlsatM", "alsat_front", ''])
		stations.append(["Kanal5", "kanal5_front", ''])
		stations.append(["HRT", "hrt_front", ''])
		stations.append(["РТС", "rts_front", ''])

		stations.append(["", "break", ''])
		stations.append(["Гледај во живо", "live_front", ''])

		for statname, statpage, fanart in stations:
			addDir(statname, statpage, '', '', fanart)

		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))


	elif page == 'live_front':
		addDir('telekabel.com.mk', 'live_telekabelmk', '', '')
		addDir('zulu.mk', 'live_zulumk', '', '')
		addDir('мрт play', 'list_mrtlive', '', 'http://mrt.com.mk/sites/all/themes/mrt/logo.png')
		addDir('serbiaplus (beta)', 'serbiaplus_front', '', 'http://www.serbiaplus.com/wp-content/uploads/2013/11/logofront.png')
		addDir('останати...', 'live_other', '', '')
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == 'serbiaplus_front':
		addDir('NEW ADDITIONS', 'serbiaplus_newadditions', '', '')
		addDir('MOST VIEWED', 'serbiaplus_mostviewed', '', '')
		addDir('', 'break', '', '')
		listing = listSerbiaPlusCategories()
		for url, title in listing:
			title=title.replace('&#8211;', '-')
			title=title.replace('&amp;', '&')
			addDir(title, 'serbiaplus_stations', url, '')
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page=='serbiaplus_stations' or page =='serbiaplus_newadditions' or page=='serbiaplus_mostviewed':
		if page=='serbiaplus_stations':
			listing = listSerbiaPlusTVs(url)
		elif page=='serbiaplus_newadditions':
			listing = listSerbiaPlusTVs('http://www.serbiaplus.com/')
		elif page=='serbiaplus_mostviewed':
			listing = listSerbiaPlusTVs('http://www.serbiaplus.com/en-cok-izlenenler/')
		for url, thumb, title in listing:
			title=title.replace('&#8211;', '-')
			title=title.replace('&amp;', '&')
			title=title.replace('&#038;', '&')
			addLink(title, url, 'playserbiaplus_stream', thumb)
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == 'playserbiaplus_stream':
		playSerbiaPlusStream(url)

	elif page == 'live_zulumk':
		listing = createZuluListing()
		#for station, thumb in match:
		#	print station, thumb
		for station, thumb in listing:
			addLink(station, 'http://on.net.mk/zulu/'+station, 'playzulustream', thumb)
		setView('files', 500)
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page=='playzulustream':
		playZuluStream(url)

	elif page == 'live_telekabelmk':
		listing = createTelekabelListing()
		for u, streamname in listing:
			if not u.startswith('mms'):
				addLink(streamname, u, 'playtelekabelstream', '')
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page=='playtelekabelstream':
		playTelekabelStream(url)

	elif page == 'live_other':
		listing = createOtherListing()
		for i in range(len(listing)):
			addLink(listing[i][0], 'u'+str(i), 'play_live_other', listing[i][2])
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == 'play_live_other':
		nr = int(url[1:])
		listing = createOtherListing()
		item=listing[nr]
		playurl(item[1])

	elif page == '24vesti_front':
		addLink('Вести', '', '24vesti_vesti', '')
		addDir('Емисии', '24vesti_emisii', '', '')
		addDir('Видео содржина', '24vesti_videosodrzina', '', '')
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == '24vesti_emisii':
		listing = create24VestiEmisiiListing(url)
		for u,thumb,title in listing:
			if title.__contains__('WIN-WIN'):
				addLink(title, u, '24vesti_playvideo', thumb,'http://a1on.mk/wordpress/wp-content/uploads/2013/01/olivera-trajkovska.jpg')
			else:
				addLink(title, u, '24vesti_playvideo', thumb)
		if url == '' or url == None:
			addDir('Претходно', '24vesti_emisii', '1', '')
		else:
			urlpage = int(url)+1
			addDir('Претходно', '24vesti_emisii', str(urlpage), '')

		setView('movies', 500)
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == '24vesti_videosodrzina':
		listing = create24VestiVideoSodrzina()
		for u,thumb,title1,title2 in listing:
			addLink(title2.strip(), u, '24vesti_playvideosodrzina', thumb)
		setView('files', 500)
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page=='24vesti_vesti':
		play24VestiVesti()

	elif page=='24vesti_playvideo':
		play24VestiVideo(url)

	elif page=='24vesti_playvideosodrzina':
		play24VestiVideo(url)

	elif page == 'novatv_front':
		addDir('Македонија', 'novatv_makedonija', '', '')
		addDir('Еврозум', 'novatv_evrozum', '', '')
		addDir('Секуловска', 'novatv_sekulovska', '', '')
		addDir('Документ', 'novatv_dokument', '', '')
		addDir('Студио', 'novatv_studio', '', '')
		addDir('Актуел', 'novatv_aktuel', '', '')
		addDir('Глобус', 'novatv_globus', '', '')
		addDir('Култура', 'novatv_kultura', '', '')
		addDir('Занимливости', 'novatv_zanimlivosti', '', '')
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page=='novatv_playvideo':
		playNovatvVideo(url)

	elif page.__contains__('novatv_'):
		listing = createNovatvListing(page)

		if page == 'novatv_evrozum':
			fanart = 'http://novatv.mk/photos/u2.jpg'
		elif page == 'novatv_sekulovska':
			fanart = 'http://novatv.mk/photos/u4.jpg'
		elif page == 'novatv_dokument':
			fanart = 'http://novatv.mk/photos/u2.jpg'
		else:
			fanart = ''
		for u,thumb,title,description,date in listing:
			addLink(title+' '+date, u, 'novatv_playvideo', 'http://novatv.mk/'+thumb, fanart)
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == "sitel_front":
		addDir('Видео', 'sitel_video', '', '')
		addLink('Дневник', '', 'sitel_dnevnik', 'http://sitel.com.mk/sites/all/themes/siteltv/images/video-dnevnik.jpg')
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == "sitel_video":
		listing = createSitelVideoListing()
		for u, thumb, title in listing:
			addLink(title, u, 'playsitelvideo',thumb)
		setView('files', 500)
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page=='playsitelvideo':
		playSitelVideo(url)

	elif page == 'sitel_dnevnik':
		playSitelDnevnik()

	elif page == "mrt_front":
		listing = createmrtfrontList()
		for url,channel in listing:
			addDir(channel, 'list_mrtchannel', url, '')
		addDir('ВО ЖИВО', 'list_mrtlive', '', '')

		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == 'list_mrtlive':
		listing = list_mrtlive()
		for url,title,thumb in listing:
			addLink(title, url, 'play_mrt_video', thumb)

		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == 'list_mrtchannel':
		listing = list_mrtchannel(url)
		for type,url,thumb,duration,title in listing:
			if type=="video":
				addLink(title, url, 'play_mrt_video', thumb, '', duration)
			elif type=="channel":
				addDir(">>  "+title, 'list_mrtchannel', url, thumb)
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == 'play_mrt_video':
		playmrtvideo(url)

	elif page == 'alsat_front':
		addDir('Последни емисии', 'alsat_15latest', '', '')
		addDir('Emisione Rruga Drejt', 'alsat_rruga', '', '')
		addDir('Emisione 15 min Debat', 'alsat_15mindebat', '', '')
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == 'alsat_rruga':
		listing = createAlsatRrugaListing()
		for title, link, thumb in listing:
			title = title.replace('&lt;', '<')
			title = title.replace('&gt;', '>')
			title = title.replace('&quot;', "'")
			title = title.replace('&#039;', "'")
			title = title.replace('&amp;', "&")

			thumb = thumb.replace('&lt;', '<')
			thumb = thumb.replace('&gt;', '>')
			thumb = thumb.replace('&quot;', "'")
			thumb = thumb.replace('&#039;', "'")
			thumb = thumb.replace('&amp;', "&")

			addLink(title, link, 'playalsatvideo', thumb)
		setView('files', 500)
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == 'alsat_15mindebat':
		listing = createAlsat15mindebatListing()
		for thumb, link, title in listing:
			title = title.replace('&lt;', '<')
			title = title.replace('&gt;', '>')
			title = title.replace('&quot;', "'")
			title = title.replace('&#039;', "'")
			title = title.replace('&amp;', "&")

			thumb = thumb.replace('&lt;', '<')
			thumb = thumb.replace('&gt;', '>')
			thumb = thumb.replace('&quot;', "'")
			thumb = thumb.replace('&#039;', "'")
			thumb = thumb.replace('&amp;', "&")

			addLink(title, 'http://alsat-m.tv/'+link, 'playalsatvideo', thumb)
		setView('files', 500)
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == 'alsat_15latest':
		listing = createAlsat15mindebatLatest()
		for thumb, link, title in listing:
			title = title.replace('&lt;', '<')
			title = title.replace('&gt;', '>')
			title = title.replace('&quot;', "'")
			title = title.replace('&#039;', "'")
			title = title.replace('&amp;', "&")

			thumb = thumb.replace('&lt;', '<')
			thumb = thumb.replace('&gt;', '>')
			thumb = thumb.replace('&quot;', "'")
			thumb = thumb.replace('&#039;', "'")
			thumb = thumb.replace('&amp;', "&")

			addLink(title, link, 'playalsatvideo', thumb)
		setView('files', 500)
		xbmcplugin.endOfDirectory(int(sys.argv[1]))



	elif page == 'playalsatvideo':
		playAlsatVideo(url)

	elif page == 'hrt_front':
		addLink('HRT1 Live', 'http://5323.live.streamtheworld.com/HTV1?streamtheworld_user=1&nobuf=1361039552824', '', 'http://upload.wikimedia.org/wikipedia/commons/1/1f/HRT1_Logo_aktuell.jpg')
		addLink('HRT4 Live', 'http://4623.live.streamtheworld.com/HRT4?streamtheworld_user=1&nobuf=1384296611008', '', 'http://images3.wikia.nocookie.net/__cb20121221162236/logopedia/images/d/dc/HRT4.png')
		addDir('', 'break', '', '')
		listing = createHRTSeriesListing()
		for link, title in listing:
			addDir(title, 'list_hrt_episodes', link, '')
		setView('files', 500)
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == 'list_hrt_episodes':
		listing = listHRTEpisodes(url)
		for title,link in listing:
			addLink(title, link, 'play_hrt_video', '')
		setView('files', 500)
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == 'play_hrt_video':
		playHRTVideo(url)

	elif page == 'kanal5_front':
		addLink('Во живо', 'mms://live.kanal5.com.mk/kanal5', '', '')
		addDir('', 'break', '', '')
		listing = createKanal5Series()
		for thumb,link,title in listing:
			addDir(title, 'list_kanal5_episodes', link, 'http://www.kanal5.com.mk/'+thumb)
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == 'list_kanal5_episodes':
		listing = listKanal5Episodes(url)
		for link,title in listing:
			title = title.replace('<span class="datum_tx"><strong>', '')
			title = title.replace('</strong>', '')
			title = title.replace('</span>', '')
			addLink(title, link, 'playKanal5Video', '')
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == 'playKanal5Video':
		playKanal5Video(url, name)

	elif page == 'rts_front':

		addLink('РТС Уживо', 'http://rts.videostreaming.rs/rts', '', 'http://www.rts.rs/upload/storyBoxImageData/2008/07/19/18865/rts%20logo.bmp')
		addLink('Радио Београд 1', 'http://rts.ipradio.rs:8002', '', '')
		addLink('Радио Београд 2/ Радио Београд 3', 'http://rts.ipradio.rs:8004', '', '')
		addLink('Радио Београд 202', 'http://rts.ipradio.rs:8006', '', '')
		addLink('Радио Београд стереорама (Викендом)', 'http://rts.ipradio.rs:8008', '', '')
		addDir('', 'break', '', '')

		content=readurl('http://www.rts.rs/page/podcast/ci.html')
		start=0
		while True:
			start=content.find('<h1>', start)
			if start != -1:
				delim=content.find('</h1>', start)
				station=content[start+4:delim]
				next=content.find('<h1>', start+4)
				if next==-1:
					next=content.find('<div id="right">', start+4)
				match=re.compile('<a href="(.+?)".*?>(.+?)</a>').findall(content[start:next])
				for url, title in match:
					addDir(station+"   "+title, 'list_rts_episodes', url, '')
				start=start+4
			else:
				break

		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == 'list_rts_episodes':
		art=''
		content=readurl('http://www.rts.rs'+url)
		metadata=re.compile('<meta name="description" content="(.+?)"').findall(content)
		if metadata != []:
			image=re.compile('src=&#034;(.+?)&#034;').findall(metadata[0])
			if image != []:
				art=image[0]

			start=0
			while True:
				start = content.find('<tr class="first"', start)
				if start == -1:
					break;
				next = content.find('<tr class="first"', start+16)
				thumb=re.compile('<img src="(.+?)"').findall(content, start)
				title=re.compile('title="(.+?)"').findall(content, start)
				uptitle=re.compile('<p class="uptitle">.*?\n(.+?)\n').findall(content, start)
				startfiles=content.find('<div class="files">', start)

				if next != -1:
					files=re.compile('<a href="(.+?)"').findall(content, startfiles, next)
				else:
					files=re.compile('<a href="(.+?)"').findall(content, startfiles)
				if title != [] and uptitle != [] and files != [] and thumb != []:
					addLink(title[0].strip()+' - '+uptitle[0].strip().replace('&nbsp;', ' '), 'http://www.rts.rs'+files[1], '', 'http://www.rts.rs'+thumb[0], art)

				start=start+16

		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))


def addLink(name,url,page,iconimage,fanart='',duration='00:00', published='0000-00-00', description=''):
        ok=True
	if page != '':
		u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&page="+str(page)+"&name="+urllib.quote_plus(name)
	else:
		u=url
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )

	if duration != '00:00':
		liz.setInfo('video', { 'Duration':duration })

	if published != '0000-00-00':
		liz.setInfo('video', {'Aired':published})

	if description != '':
		liz.setInfo('video', { 'plot':description })

	#liz.setProperty('IsPlayable', 'false')
	if fanart!='':
		liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok

def addDir(name,page,url,iconimage,fanart=''):
        u=sys.argv[0]+"?page="+urllib.quote_plus(page)+"&url="+urllib.quote_plus(url)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
	if fanart!='':
		liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

params=get_params()
url=None
name=None
page=None

#for i in range(0,4):
#	try:
#		print "arg["+str(i)+"]"+str(sys.argv[i])
#	except:
#		pass

# Inspired by xbmc-iplayer2

old_version = ''

if os.path.isfile(VERSION_FILE):
	old_version = fread(VERSION_FILE)

if old_version != __version__:
	result = registerVersion(__version__)
	#result = True
	if result:
		fwrite(VERSION_FILE, __version__)
result = True

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass

try:
        name=urllib.unquote_plus(params["name"])
except:
        pass

try:
	page=urllib.unquote_plus(params["page"])
except:
        pass

if result:
	PROCESS_PAGE(page, url, name)

