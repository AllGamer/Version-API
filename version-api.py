from flask import Flask, redirect, jsonify, render_template
import json
import ast
import requests
import redis
from datetime import datetime
from BeautifulSoup import BeautifulSoup, SoupStrainer
import re

app = Flask(__name__)
r = redis.StrictRedis(host='localhost', port=6379, db=0)


@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/minecraft/server/download/<version>')
def minecraft_server_url(version):
    if r.get('last_minecraft_update') is None:
        minecraft_cache_update()
    print 'Last updated on %s' % r.get('last_minecraft_update')
    if version == 'latest':
        minecraft_version = r.get('latest_minecraft_server')
    elif version == 'snapshot':
        minecraft_version = r.get('snapshot_minecraft_server')
    else:
        minecraft_version = version
    minecraft_download = 'https://s3.amazonaws.com/Minecraft.Download/versions/'+minecraft_version+'/minecraft_server.'+minecraft_version+'.jar'
    return redirect(minecraft_download)


@app.route('/minecraft/server/versions')
def minecraft_server_versions():
    print r.get('minecraft_versions_list')
    if r.get('minecraft_versions_list') is not None:
        return r.get('minecraft_versions_list')
    else:
        minecraft_versions_list_update()
        return r.get('minecraft_versions_list')


@app.route('/minecraft/client/download/<version>')
def minecraft_client_url(version):
    if r.get('last_minecraft_update') is None:
        minecraft_cache_update()
    print 'Last updated on %s' % r.get('last_minecraft_update')
    if version == 'latest':
        minecraft_version = r.get('latest_minecraft_client')
    elif version == 'snapshot':
        minecraft_version = r.get('snapshot_minecraft_client')
    elif version == 'beta':
        minecraft_version = r.get('beta_minecraft_client')
    else:
        minecraft_version = version
    minecraft_download = 'https://s3.amazonaws.com/Minecraft.Download/versions/'+minecraft_version+'/'+minecraft_version+'.jar'
    return redirect(minecraft_download)

@app.route('/minecraft/json')
def display_minecraft_versions():
    if r.get('last_minecraft_update') is None:
        minecraft_cache_update()
    m_json = ast.literal_eval(r.get('minecraft_json'))
    return jsonify(m_json)


@app.route('/minecraft')
def minecraft_index():
    return render_template('minecraft_index.html')


@app.route('/sourcemod')
def sourcemod_index():
    return render_template('sourcemod_index.html')


@app.route('/metamod')
def metamod_index():
    return render_template('metamod_index.html')


def minecraft_cache_update():
    r.setex('last_minecraft_update', 900, datetime.now())
    minecraft_json = requests.get('https://s3.amazonaws.com/Minecraft.Download/versions/versions.json').json()
    latest = minecraft_json['latest']['release']
    snapshot = minecraft_json['versions'][0]['id']
    r.set('minecraft_json', minecraft_json)
    r.set('latest_minecraft_client', latest)
    r.set('latest_minecraft_server', latest)
    r.set('snapshot_minecraft_client', snapshot)
    r.set('snapshot_minecraft_server', snapshot)
    version_id = minecraft_json['versions'][0]['id']
    for v in minecraft_json['versions']:
        if v['type'] == 'old_beta':
            version_id = v['id']
            break
    r.set('beta_minecraft_client', version_id)
    return


def minecraft_versions_list_update():
    versions_list = []
    for element in ast.literal_eval(r.get('minecraft_json'))['versions']:
        if element['type'] == 'snapshot' or element['type'] == 'release' or element['type'] == 'old_beta':
            version = '%s-%s' % (element['id'], element['type'])
            versions_list.append(version)
    versions_list = ' '.join(versions_list)
    r.setex('minecraft_versions_list', 900, versions_list)
    return


@app.route('/sourcemod/download/<platform>/stable/<version>')
def sourcemod_stable(platform, version):
    if platform == 'linux':
        latest_stable = 'http://www.sourcemod.net/smdrop/1.7/sourcemod-latest-linux'
        latest_stable = requests.get(latest_stable).text
        if version != 'latest':
            sourcemod_download = 'http://www.sourcemod.net/smdrop/1.7/'+version
        else:
            sourcemod_download = 'http://www.sourcemod.net/smdrop/1.7/'+latest_stable
        return redirect(sourcemod_download)
    if platform == 'windows':
        latest_stable = 'http://www.sourcemod.net/smdrop/1.7/sourcemod-latest-windows'
        latest_stable = requests.get(latest_stable).text
        if version != 'latest':
            sourcemod_download = 'http://www.sourcemod.net/smdrop/1.7/'+version
        else:
            sourcemod_download = 'http://www.sourcemod.net/smdrop/1.7/'+latest_stable
        return redirect(sourcemod_download)
    if platform == 'mac':
        latest_stable = 'http://www.sourcemod.net/smdrop/1.7/sourcemod-latest-mac'
        latest_stable = requests.get(latest_stable).text
        if version != 'latest':
            sourcemod_download = 'http://www.sourcemod.net/smdrop/1.7/'+version
        else:
            sourcemod_download = 'http://www.sourcemod.net/smdrop/1.7/'+latest_stable
        return redirect(sourcemod_download)


@app.route('/sourcemod/download/<platform>/dev/<version>')
def sourcemod_dev(platform, version):
    if platform == 'linux':
        latest_dev = 'http://www.sourcemod.net/smdrop/1.8/sourcemod-latest-linux'
        latest_dev = requests.get(latest_dev).text
        if version != 'latest':
            sourcemod_download = 'http://www.sourcemod.net/smdrop/1.8/'+version
        else:
            sourcemod_download = 'http://www.sourcemod.net/smdrop/1.8/'+latest_dev
        return redirect(sourcemod_download)
    if platform == 'windows':
        latest_dev = 'http://www.sourcemod.net/smdrop/1.8/sourcemod-latest-windows'
        latest_dev = requests.get(latest_dev).text
        if version != 'latest':
            sourcemod_download = 'http://www.sourcemod.net/smdrop/1.8/'+version
        else:
            sourcemod_download = 'http://www.sourcemod.net/smdrop/1.8/'+latest_dev
        return redirect(sourcemod_download)
    if platform == 'mac':
        latest_dev = 'http://www.sourcemod.net/smdrop/1.8/sourcemod-latest-mac'
        latest_dev = requests.get(latest_dev).text
        if version != 'latest':
            sourcemod_download = 'http://www.sourcemod.net/smdrop/1.8/'+version
        else:
            sourcemod_download = 'http://www.sourcemod.net/smdrop/1.8/'+latest_dev
        return redirect(sourcemod_download)


@app.route('/metamod/download/<platform>')
def metamod_latest(platform):
    response = requests.get('https://www.metamodsource.net/downloads/', verify=False).content
    links = []
    for l in BeautifulSoup(response, parseOnlyThese=SoupStrainer('a')):
        links.append(l['href'])

    links_list = []
    for link in links:
        match = re.match(r'(?im)^downloads/mmsource-(.+?)-(windows\.zip|linux\.tar\.gz|mac\.zip)$', link)
        if match:
            links_list.append(match.group())

    windows, linux, mac = None, None, None
    for v in links_list:
        if v.find('windows') != -1:
            windows = v
        elif v.find('linux') != -1:
            linux = v
        else:
            mac = v
    if platform == 'windows':
        if windows is not None:
            metamod_download = 'https://www.metamodsource.net/'+windows
            return redirect(metamod_download)
        else:
            return 'Error finding file'
    if platform == 'linux':
        if windows is not None:
            metamod_download = 'https://www.metamodsource.net/'+linux
            return redirect(metamod_download)
        else:
            return 'Error finding file'
    else:
        if windows is not None:
            metamod_download = 'https://www.metamodsource.net/'+mac
            return redirect(metamod_download)
        else:
            return 'Error finding file'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
