# -*- coding: utf-8 -*- 

import urllib,urllib2,re,xbmcplugin,xbmcgui,HTMLParser

user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:11.0) Gecko/20100101 Firefox/11.0'
str_accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'

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
	pDialog.update(30, 'Fetching video stream 1')
	response = urllib2.urlopen(req)
	link = response.read()
	response.close()

	nextframematch = re.compile('name="iframe"\n\t\tsrc="(.+?)"').findall(link)

	req = urllib2.Request('http://telekabel.com.mk'+nextframematch[0])
	req.add_header('User-Agent', user_agent)
	req.add_header('Accept', str_accept)
	pDialog.update(60, 'Fetching video stream 2')
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


def PROCESS_PAGE(page,url=''):

	if page == None:
		addDir('Телевизија', 'tv_front', '', '')
		addDir('Радио', 'radio_front', '', '')
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == "radio_front":
		addDir("Слушај во живо", "liveradio_front", '', '', '')
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == "liveradio_front":
		addDir('on.net.mk', 'liveradio_onnet', '', '')
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page == "liveradio_onnet":
		listing = createOnnetRadioListing()
		for radioid,rtmstream,descr,mp3stream in listing:
			#print descr+' '+stream
			addLink(descr+' (rtmp)', 'rtmp://217.16.82.2/radio app=radio pageUrl=http://on.net.mk swfUrl=http://on.net.mk/radio/player/player.swf live=true playpath='+rtmstream+' timeout=3 swfVfy=true', '', '')
			addLink(descr+' (mp3)', mp3stream, '', '')
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))


	elif page == "tv_front":
		stations = []
		stations.append(["Мактел", "maktel_front", ''])
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
		addDir('zulu.mk', 'live_zulumk', '', '')
		addDir('telekabel.com.mk', 'live_telekabelmk', '', '')
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
		for u, name in listing:
			if not u.startswith('mms'):
				addLink(name, u, 'playtelekabelstream', '')
		setView()
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	elif page=='playtelekabelstream':
		playTelekabelStream(url)

	elif page=='playmaktelvideo':
		playMaktelVideo(url)


def addLink(name,url,page,iconimage,fanart=''):
        ok=True
	if page != '':
		u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&page="+str(page)
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

for i in range(0,4):
	try:
		print "arg["+str(i)+"]"+str(sys.argv[i])
	except:
		pass

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

PROCESS_PAGE(page, url)

