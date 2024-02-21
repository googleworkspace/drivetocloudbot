#!/usr/bin/python3

"""
Copyright 2024 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Receives an input chat message via Google Chat, then processes and sends a reply back to the user
"""

import json
import os
import uuid

from flask import Flask, request
from google.cloud import dialogflowcx_v3
import google.auth
from google.oauth2 import service_account
from storageservice import Storage
from drivewatch import DriveWatch
from checkfolder import trigger_drive_watch
from initialize import ApiEnable

# Initialize Flask app
app = Flask(__name__)


# Generates an answer from question sent to Conversational AI
def generate_answer(prompt, agent):
  # Construct session to interact with DialogFlow API

  agent = f'projects/{os.environ.get("PROJECT")}/locations/global/agents/{agent}'
  session_id = uuid.uuid4()
  session_path = f'{agent}/sessions/{session_id}'
  # Call DialogFlow CX API https://cloud.google.com/dialogflow/cx/docs/quick/api#detect-intent-python
  credentials, project_id = google.auth.default()
  client = dialogflowcx_v3.SessionsClient(credentials=credentials)

  query_input = dialogflowcx_v3.QueryInput()
  query_input.text.text = prompt
  query_input.language_code = 'en-us'
  dfcx_request = dialogflowcx_v3.DetectIntentRequest(
      session=session_path,
      query_input=query_input,
  )

  # Make the request, then return answer
  response = client.detect_intent(request=dfcx_request)
  result = response.query_result
  answer = dialogflowcx_v3.types.session.QueryResult.to_json(result)
  return json.loads(answer)

@app.route('/', methods=['GET'])
def get_handler():
  """Initial Setup."""
  _init()
  return 'Hello World'

@app.route('/watch', methods=['GET'])
def trigger_drive_watch_route():
  """Checks the drive folder for modifications."""
  trigger_drive_watch()
  return 'Triggered Drive Watch'

@app.route('/chat', methods=['POST'])
def chat_bot():
  return handler()

def handler():
  """Chat Bot Handler.

    Returns:
        Tuple of response message and status code
  """
  agent = os.environ.get('AGENT_ID')
  # Retrieve JSON input from request body
  event_data = request.get_json(silent=False)

  # Return error if payload has invalid data (not an event sent by the Google Chat API)
  if 'space' not in event_data:
      return 'This service only processes messages from Google Chat', 400

  # Parse message text/components
  text = first = None
  if 'message' in event_data and 'argumentText' in event_data['message']:  # for space/room
      text = event_data['message']['argumentText'].strip()
  elif 'message' in event_data and 'text' in event_data['message']:  # for direct message
      text = event_data['message']['text'].strip()
  if text:
      first = text.split()[0].lower()

  # Print help message
  if first in ('?', 'hi', 'hello', 'help', 'hey', 'start', 'test', '/help'):
      if event_data['space']['type'] == 'DM':
          name = event_data['user']['displayName'].split()[0]
      else:  # 'ROOM'
          name = f"<{event_data['user']['name']}>"  # 'users/[USER_ID]'
      output_message = f'Hi *{name}*! As a demo, ask a question on the data trained for the bot.'

  # Query Dialogflow for LLM answer
  else:
      answer = generate_answer(text, agent)
      responses = answer['responseMessages']
      output_message = responses[0]['text']['text'][0]

      if output_message == 'Indexing didn\'t finish yet, please come back in a few hours.':
          output_message = 'Sorry, I can\'t help you with that.'
      elif len(responses) > 1 and 'payload' in responses[1]:
          content = responses[1]['payload']['richContent'][0][0]
          action_link = None
          for k, v in content.items():
              if k == 'actionLink':
                  action_link = v
                  break
          output_message += f'\n{action_link}'
          print(f'response {output_message}')
  return {'text': output_message}, 200

def _init():
  for api in ['iam.googleapis.com','dialogflow.googleapis.com','datastore.googleapis.com','discoveryengine.googleapis.com','drive.googleapis.com']:
    ApiEnable().enable_api(project_id=os.environ.get('PROJECT'), api=api)
  storage = Storage().check_storage(bucket_name=f"{os.environ.get('PROJECT')}_{os.environ.get('BUCKET_NAME')}")

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
