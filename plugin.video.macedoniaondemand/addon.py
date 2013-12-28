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
DIR_USERDATA = xbmc.translatePath(xbmcaddon.Addon("plugin.video.macedoniaondemand").getAddonInfo('profile'))
VERSION_FILE = DIR_USERDATA+'version.txt'
__version__ = xbmcaddon.Addon("plugin.video.macedoniaondemand").getAddonInfo("version")

if not os.path.isdir(DIR_USERDATA):
	os.makedirs(DIR_USERDATA)

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

def setView(content='movies', mode=502):
	xbmcplugin.setContent(int(sys.argv[1]), content)
	xbmc.executebuiltin("Container.SetViewMode("+str(mode)+")")


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
	listitem = xbmcgui.ListItem(titlematch[0] + ' - ВО ЖИВО');

	play=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	play.clear()
	play.add(streammatch[0], listitem)
	player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
	pDialog.update(80, 'Playing')
	player.play(play)
	pDialog.close()

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

	#titlematch = re.compile('class="title">(.+?)</h1>').findall(link)
	#listitem = xbmcgui.ListItem(titlematch[0] + ' - ВО ЖИВО')
	listitem = xbmcgui.ListItem('Телекабел стриминг во живо')

	play=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	play.clear()
	play.add(streammatch[0], listitem)
	player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
	pDialog.update(80, 'Playing')
	player.play(play)
	pDialog.close()

	return True


# MAKTEL methods

def createMaktelListing():
	url='http://maktel.mk/'

	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	match=re.compile('\t\t\t\t\t\t<div class = \'item\' id = \'.+?\'>\r\n\t\t   \t<a href="(.+?)" class="fancybox fancybox.ajax">\r\n\t\t   \t\t  \t   \t<img class = \'image\' src="(.+?)" width="319" height="260" /><img src="images/play1.png" style="position:absolute;margin-top:60px;margin-left:80px;" />  \t  \t   \t</a> \r\n.+?<div class = \'text\'>\r\n\t\t\t<div class = \'title\'>\r\n\t\t    <div class = \'desc\'>\r\n\t\t   \t<span>(.+?)</span>\r\n\t\t\t</div>\t\r\n\t\t\t</div>\r\n\t\t    </div>\r\n\t\t\t</div>').findall(link)

	#for link, thumb, descr in match:
	#	print descr

	return match

def playMaktelVideo(url):
	pDialog = xbmcgui.DialogProgress()
	pDialog.create('Maktel Video', 'Initializing')

	listitem = xbmcgui.ListItem('Maktel Video');

	play=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	play.clear()
	if url.__contains__('youtube'):
		play.add('plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid='+url.split('/')[4], listitem)
	else:
		play.add(url, listitem)
	player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)

	pDialog.update(60, 'Playing')
	player.play(play)
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
	match=re.compile('<a id=".+?" data-stream="(.+?)" data-frequency="(.+?)">(.+?)</a>').findall(link)
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

	listitem = xbmcgui.ListItem('24vesti.com.mk - Вести')

	play=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	play.clear()
	play.add('http://24vesti.com.mk'+match[0]+'|Cookie=macedoniaondemand', listitem)
	player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
	pDialog.update(80, 'Playing')
	player.play(play)
	pDialog.close()
	return True

def create24VestiEmisiiListing(urlpagenr):
	if urlpagenr == '':
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
	listitem = xbmcgui.ListItem(titlematch[0]);

	play=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	play.clear()
	if filematch[0].__contains__('dailymotion'):
		play.add('plugin://plugin.video.dailymotion_com/?url='+filematch[0].split('/')[-1]+'&mode=playVideo', listitem)
	elif filematch[0].__contains__('youtube'):
		play.add('plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid='+filematch[0].split('/')[-1], listitem)
	else:
		play.add(filematch[0], listitem)
	player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)

	pDialog.update(60, 'Playing')
	player.play(play)
	pDialog.close()

	return True


# NOVATV methods

def createNovatvListing(page):
	url = 'http://novatv.mk/index.php?navig=8&cat='

	if page == 'novatv_evrozum':
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
	listitem = xbmcgui.ListItem(titlematch[0]);
	play=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	play.clear()
	play.add(streammatch[0], listitem)
	player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
	pDialog.update(60, 'Playing')
	player.play(play)
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
	listitem = xbmcgui.ListItem(titlematch[0]);

	play=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	play.clear()
	if filematch[0].__contains__('rtmp'):
		rtmpurl = filematch[0]
		app=rtmpurl.split('/')[3]+'/'
		apos=rtmpurl.find(app)
		y=rtmpurl[apos+len(app):]
		play.add(rtmpurl[:apos+len(app)]+' app='+app+' pageUrl=http://sitel.com.mk swfUrl=http://sitel.com.mk/sites/all/libraries/jw.player/jwplayer.flash.swf playpath='+y+' swfVfy=true flashver="LNX 10,0,32,18"', listitem)
	else:
		play.add(filematch[0], listitem)
	player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
	pDialog.update(90, 'Playing')
	player.play(play)
	pDialog.close()

	return True

def playSitelDnevnik():
	listitem = xbmcgui.ListItem('Сител Дневник')
	play=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	play.clear()
	#play.add('http://sitel.com.mk/sites/default/files/dnevnik/dnevnik/dnevnik.mp4', listitem)
	play.add('rtmp://video.sitel.com.mk/vod/ app=vod/ pageUrl=http://sitel.com.mk swfUrl=http://sitel.com.mk/sites/all/libraries/jw.player/jwplayer.flash.swf playpath=mp4:default/files/dnevnik/dnevnik/dnevnik.mp4 swfVfy=true flashver="LNX 10,0,32,18"', listitem)
	player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
	player.play(play)

	return True

#  MTV methods

def createMTVSeriesListing():
	url='http://www.mtv.com.mk/liveVideos.aspx?aId=undefined'
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req, timeout=30)
	link=response.read()
	response.close()
	return link

#  OTHER live streams methods

def createOtherListing():
	list=[]
	list.append(['HRT1', 'http://5323.live.streamtheworld.com/HTV1?streamtheworld_user=1&nobuf=1361039552824', 'http://www.247webtv.com/wp-content/uploads/2012/05/hrt1.jpg'])
	list.append(['RTS SAT', 'http://rts.videostreaming.rs/rts', 'http://www.rts.rs/upload/storyBoxImageData/2008/07/19/18865/rts%20logo.bmp'])
	list.append(['HRT4', 'http://4623.live.streamtheworld.com/HRT4?streamtheworld_user=1&nobuf=1384296611008', 'http://images3.wikia.nocookie.net/__cb20121221162236/logopedia/images/d/dc/HRT4.png'])
	list.append(['Russia Today News HD', 'rtmp://rt.fms-04.visionip.tv/live app=live swfUrl=http://rt.com/s/swf/player5.4.viral.swf pageUrl=http://rt.com playpath=rt-global-live-HD live=1 swfVfy=true', 'http://rt.com/static/img/static/logo.jpg'])
	list.append(['Russia Today America HD', 'rtmp://rt.fms-04.visionip.tv/live app=live swfUrl=http://rt.com/s/swf/player5.4.viral.swf pageUrl=http://rt.com playpath=rt-america-live-HD live=1 swfVfy=true', 'http://rt.com/static/img/static/logo.jpg'])
	list.append(['Al Jazeera Balkans', 'rtmp://aljazeeraflashlivefs.fplive.net/aljazeeraflashlive-live app=aljazeeraflashlive-live swfUrl=http://www.nettelevizor.com/playeri/player.swf pageUrl=http://ex-yu-tv-streaming.blogspot.se playpath=aljazeera_balkans_high live=true swfVfy=true', 'http://balkans.aljazeera.net/profiles/custom/themes/aljazeera_balkans/images/banner.png'])
	list.append(['Heart TV UK', 'rtmp://cdn-sov-2.musicradio.com:80/LiveVideo//Heart', 'http://www.jumpdesign.co.uk/assets/templates/jump/videos/placeholder/heart_2.jpg'])
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
	#match=re.compile('<div class="short">\n\t\t<div class="short_holder">\n\t\t\t\n\t\t\t\t<div class="image3">\n  \n\t\t\t\t\t<a href="(.+?)">  <div class="video_icon"> <img src=".+?" alt="Video" />\t</div><img src="(.+?)" alt="image" /><br /></a>\n\t\t\t\t</div>\n\n\t\t\t\n\t\t\t<h2> <a href="(.+?)">(.+?)</a></h2>\n\t\t\t<span class="summary">(.+?)</span>...\n\t\t\t<div class="article_link">\n\t\t\t\t\n\t\t\t\t\t\n\t\t\t\t\t\t<a href="(.+?)">.+?</a>').findall(link)
	#match=re.compile('<div class="short">\n\t\t<div class="short_holder">\n\t\t\t\n\t\t\t\t<div class="image3">\n  \n\t\t\t\t\t<a href="(.+?)">  <div class="video_icon"> <img src=".+?" alt="Video" />\t</div><img src="(.+?)" alt="image" /><br /></a>\n\t\t\t\t</div>\n\n\t\t\t\n\t\t\t<h2> <a href=".+?">(.+?)</a></h2>\n\t\t\t<span class="summary">.+?</span>...\n\t\t\t<div class="article_link">\n\t\t\t\t\n\t\t\t\t\t\n\t\t\t\t\t\t<a href=".+?">.+?</a>').findall(link)
	match=re.compile('<div class="video_short">\n        \n                \n            \n        <div class="image_play">\n            <a id=".+?" href=".+?>\n                \n                    <img src="(.+?)" alt=".+?" />\n                    \n                \n            </a>\n        </div>\n        <h4><a href="(.+?)">(.+?)</a></h4>').findall(link[link.find('<div id="videos_latest">'):link.find('<div id="videos_most_popular">')])

	return match

def createAlsat15mindebatLatest():
	url = 'http://alsat.mk/index.php/emisii/index.1.html'
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	link = response.read()
	response.close()
	#match=re.compile('<div class="short">\n\t\t<div class="short_holder">\n\t\t\t\n\t\t\t\t<div class="image3">\n  \n\t\t\t\t\t<a href="(.+?)">  <div class="video_icon"> <img src=".+?" alt="Video" />\t</div><img src="(.+?)" alt="image" /><br /></a>\n\t\t\t\t</div>\n\n\t\t\t\n\t\t\t<h2> <a href="(.+?)">(.+?)</a></h2>\n\t\t\t<span class="summary">(.+?)</span>...\n\t\t\t<div class="article_link">\n\t\t\t\t\n\t\t\t\t\t\n\t\t\t\t\t\t<a href="(.+?)">.+?</a>').findall(link)
	#match=re.compile('<div class="short">\n\t\t<div class="short_holder">\n\t\t\t\n\t\t\t\t<div class="image3">\n  \n\t\t\t\t\t<a href="(.+?)">  <div class="video_icon"> <img src=".+?" alt="Video" />\t</div><img src="(.+?)" alt="image" /><br /></a>\n\t\t\t\t</div>\n\n\t\t\t\n\t\t\t<h2> <a href=".+?">(.+?)</a></h2>\n\t\t\t<span class="summary">.+?</span>...\n\t\t\t<div class="article_link">\n\t\t\t\t\n\t\t\t\t\t\n\t\t\t\t\t\t<a href=".+?">.+?</a>').findall(link)
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
	listitem = xbmcgui.ListItem(titlematch[0]);

	play=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	play.clear()
	if filematch[0].__contains__('youtu.be'):
		play.add('plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid='+filematch[0].split('/')[-1].strip(), listitem)
	else:
		play.add(filematch[0], listitem)
	player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
	pDialog.update(90, 'Playing')
	player.play(play)
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
	match=re.compile('<li><a href="(.+?)">(.+?)</a></li>\n                                    \n                                        ').findall(link)
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
	listitem = xbmcgui.ListItem(titlematch[0]);

	play=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	play.clear()
	if filematch[0].__contains__('youtu.be'):
		play.add('plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid='+filematch[0].split('/')[-1].strip(), listitem)
	else:
		play.add(filematch[0], listitem)
	player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
	pDialog.update(90, 'Playing')
	player.play(play)
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

	listitem = xbmcgui.ListItem(name+' ')

	play=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	play.clear()
	play.add(match[1]+'|Cookie=macedoniaondemand', listitem)
	player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
	pDialog.update(80, 'Playing')
	player.play(play)
	pDialog.close()
	return True


# general methods

def registerVersion(ver):
	result = True
	url = 'http://macedoniaondemand.com/register_plugin.php?ver='+ver
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	try:
		response = urllib2.urlopen(req)
		link = response.read()
		response.close()
	except:
		result = False
	return result

def PROCESS_PAGE(page,url='',name=''):

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
		total=0
		count=0
		for stream, freq, title in listing:
			total=total+1

		for stream, freq, title in listing:
			#print freq+" "+name+" "+stream
			count=count+1
			if count > total/2:
				addLink(freq+" "+title, 'rtmp://off.net.mk/radio app=radio pageUrl=http://off.net.mk swfUrl=http://off.net.mk/sites/all/libraries/jwplayer/player.swf live=true playpath='+stream+' timeout=3 swfVfy=true', '', '')
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))


	elif page == "tv_front":
		stations = []
		#stations.append(["Мактел", "maktel_front", ''])
		stations.append(["24 Вести", "24vesti_front", ''])
		stations.append(["НОВА ТВ", "novatv_front", ''])
		stations.append(["Сител", "sitel_front", ''])
		stations.append(["МТВ", "mtv_front", ''])
		stations.append(["AlsatM", "alsat_front", ''])
		stations.append(["HRT", "hrt_front", ''])
		stations.append(["Kanal5", "kanal5_front", ''])


		stations.append(["", "break", ''])
		stations.append(["Гледај во живо", "live_front", ''])

		for statname, statpage, fanart in stations:
			addDir(statname, statpage, '', '', fanart)

		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))


	elif page == 'maktel_front':
		listing = createMaktelListing()
		for link, thumb, title in listing:
			# instead of a link we'll use thumb -> easy to construct youtube link from it
			addLink(title, thumb, 'playmaktelvideo', thumb)
		setView('files', 500)
		xbmcplugin.endOfDirectory(int(sys.argv[1]))


	elif page == 'live_front':
		addDir('telekabel.com.mk', 'live_telekabelmk', '', '')
		addDir('zulu.mk', 'live_zulumk', '', '')
		addDir('останати...', 'live_other', '', '')
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

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
		listitem = xbmcgui.ListItem(item[0])
		play=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		play.clear()
		play.add(item[1], listitem)
		player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
		player.play(play)

	elif page=='playmaktelvideo':
		playMaktelVideo(url)

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
		if url == '':
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
			fanart = 'http://it.com.mk/wp-content/themes/itcommkv3/js/timthumb.php?src=http://it.com.mk/wp-content/uploads/2013/01/178960_10150985004651873_892876810_n.jpg&w=640&h=250&zc=1&q=100'
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

	elif page == "mtv_front":
		addDir('МТВ Емисии','mtv_emisii','','')
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == 'mtv_emisii':
		link = createMTVSeriesListing()
		tree = BeautifulSoup(link)

		for Series in tree.findAll('gallery'):
			SeriesName = Series.get('name')
			for Videos in Series.findAll('video'):
				VideoTitle = Videos.get('title')
				VideoThumb = Videos.get('thumb')
				VideoLink = Videos.get('videoclip')
				addLink(SeriesName+" - "+VideoTitle, 'http://www.mtv.com.mk/'+VideoLink, '', VideoThumb)

		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

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
		listing = createHRTSeriesListing()
		for link, title in listing:
			addDir(title, 'list_hrt_episodes', link, '')
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == 'list_hrt_episodes':
		listing = listHRTEpisodes(url)
		for title,link in listing:
			addLink(title, link, 'play_hrt_video', '')
		setView()
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

def addLink(name,url,page,iconimage,fanart=''):
        ok=True
	if page != '':
		u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&page="+str(page)+"&name="+urllib.quote_plus(name)
	else:
		u=url
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
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

