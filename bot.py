"""Example bot that returns a synchronous response."""

from flask import Flask, request, json
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account
cred = credentials.Certificate('myprojects-8414e-firebase-adminsdk-dmfos-94a059fec5.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

scopes = 'https://www.googleapis.com/auth/chat.bot'
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'sinuous-env-260912-56792504c8df.json', scopes)
chat = build('chat', 'v1', http=credentials.authorize(Http()))

app = Flask(__name__)

@app.route('/test', methods=['GET'])
def test():
  return 'ok'

@app.route('/', methods=['POST'])
def on_event():
  event = request.get_json()
  spaces = chat.spaces().list().execute()
  if event['message']['sender']['email'] == 'gabriel.azevedo@iv2.com.br':
    cmd = event['message']['text'].split()
    if cmd[0] == 'msg':
      send_inside_msg(cmd[1], cmd[2])
    elif cmd[0] == 'proj':
      return proj_controller(cmd[1], cmd[2], ''.join(cmd[3:]))

@app.route('/msg', methods=['POST'])
def send_msg():
  json = request.get_json(silent=True)
  resp = chat.spaces().messages().create(
    parent='spaces/'+json['room'], # use your space here
    body={'text': json['message']}).execute()

@app.route('/db', methods=['GET'])
def get_projects():
  projetos = db.collection('projetos').stream()
  for proj in projetos:
    print(u'{} => {}'.format(proj.id, proj.to_dict()))
  return 'ok'

def send_inside_msg(roomId, msg):
  room = find_space(roomId)
  resp = chat.spaces().messages().create(
    parent='spaces/'+room, # use your space here
    body={'text': msg}).execute()

def proj_controller(comm, proj, val):
  if comm == 'status':
    if val == 'get':
      return get_proj_status(proj)
    elif val != 'get':
      return update_proj_status(proj, val)

def get_proj_status(proj):
  projects = db.collection(u'projetos').where(u'nome', u'==', proj).stream()
  for project in projects:
    texto = (u'{} => {}'.format(project.id, project.to_dict()))
    chat.spaces().messages().create(
      parent='spaces/qIGoSgAAAAE', # use your space here
      body={'text': texto}).execute()
  return 'ok'

def update_proj_status(proj, val):
  projects = db.collection(u'projetos').where(u'nome', u'==', proj).stream()
  for project in projects:
    print(u'{} => {}'.format(project.id, project.to_dict()))
    db.collection(u'projetos').document(project.id).update({
      "status": val
    })
    return get_proj_status(proj)
  return 'error'

def find_space(room):
  print(room)
  spaces = chat.spaces().list().execute()
  print(space['displayName'])
  for space in spaces:
    if space['displayName'].lower() == room.lower():
      return space['name']

if __name__ == '__main__':
  app.run(port=5000)