from flask import Flask, redirect, jsonify
import json
import requests

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'What are you looking for?'

@app.route('/minecraft/server/download/<version>')
def minecraft_server_url(version):
    minecraft_json = requests.get('https://s3.amazonaws.com/Minecraft.Download/versions/versions.json').json()
    if version == 'latest':
        minecraft_version = minecraft_json['latest']['release']
    elif version == 'snapshot':
        minecraft_version = minecraft_json['versions'][0]['id']
    else:
        minecraft_version = version
    minecraft_download = 'https://s3.amazonaws.com/Minecraft.Download/versions/'+minecraft_version+'/minecraft_server.'+minecraft_version+'.jar'
    return redirect(minecraft_download)


@app.route('/minecraft/client/download/<version>')
def minecraft_client_url(version):
    minecraft_json = requests.get('https://s3.amazonaws.com/Minecraft.Download/versions/versions.json').json()
    if version == 'latest':
        minecraft_version = minecraft_json['latest']['release']
    elif version == 'snapshot':
        minecraft_version = minecraft_json['versions'][0]['id']
    elif version == 'beta':
        version_id = minecraft_json['versions'][0]['id']
        for v in minecraft_json['versions']:
            if v['type'] == 'old_beta':
                version_id = v['id']
                break
        minecraft_version = version_id
    else:
        minecraft_version = version
    minecraft_download = 'https://s3.amazonaws.com/Minecraft.Download/versions/'+minecraft_version+'/'+minecraft_version+'.jar'
    return redirect(minecraft_download)

@app.route('/minecraft')
def display_minecraft_versions():
    minecraft_json = requests.get('https://s3.amazonaws.com/Minecraft.Download/versions/versions.json').json()
    return jsonify(minecraft_json)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
