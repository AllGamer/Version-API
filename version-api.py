from flask import Flask, redirect, jsonify, render_template
import json
import ast
import requests
import redis
from datetime import datetime

app = Flask(__name__)
r = redis.StrictRedis(host='version.allgamer.net', port=6379, db=0)


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
