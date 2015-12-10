import requests
from BeautifulSoup import BeautifulSoup, SoupStrainer
import re


response = requests.get('http://www.metamodsource.net/downloads/').content
links = []
for l in BeautifulSoup(response, parseOnlyThese=SoupStrainer('a')):
    links.append(l['href'])

links_list = []
for link in links:
    match = re.match(r'(?im)^\/downloads\/mmsource-(.+?)-(windows\.zip|linux\.tar\.gz|mac\.zip)$', link)
    if match:
        links_list.append(match.group())
linux, windows, mac = None, None, None
for link in links_list:
    links = []
    response = requests.get('http://www.metamodsource.net'+link).content
    for l in BeautifulSoup(response, parseOnlyThese=SoupStrainer('a')):
        links.append(l['href'])

    for line in links:
        match = re.match(r'(?im)^http:(.+?)-(windows\.zip|linux\.tar\.gz|mac\.zip)$', line)
        if match:
            if match.group().find('windows') != -1:
                windows = match.group()
            if match.group().find('linux') != -1:
                linux = match.group()
            else:
                mac = match.group()
            break
print mac
print windows
print linux