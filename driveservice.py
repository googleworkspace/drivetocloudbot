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

Drive service.
"""

import io

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload


class Drive:
  """Drive Service."""

  def __init__(self):
    self.creds, _ = google.auth.default()
    self.service = build("drive", "v3", credentials=self.creds)

  def get_drive_blob(self, file_id:str='', mime_type:str=''):
    if not file_id: return

    try:
      if "google" in mime_type:
        print("exporting google file type")
        request = self.service.files().export_media(
          fileId=file_id, mimeType="application/pdf"
        ).execute()
        return request
      else:
        print("exporting to bytes")
        request = self.service.files().get_media(fileId=file_id)


      file = io.BytesIO()
      downloader = MediaIoBaseDownload(file, request)
      done = False
      while done is False:
        status, done = downloader.next_chunk()

    except HttpError as error:
      print(f"An error occurred: {error}")
      file = None

    if not file:
      return

    return file.getvalue()

  def list_folders(self, folder_ids:list=[]):
    if not folder_ids: return
    join_query = ""
    for folder_id in folder_ids:
      join_query+=f"'{folder_id}' in parents"

    query = f"({join_query}) and trashed = false and mimeType = 'application/vnd.google-apps.folder'"
    page_token = None
    while True:
      results = self.service.files().list(
        q=query,
        pageSize=10,
        fields="nextPageToken, files(id)",
        pageToken=page_token
      ).execute()
      page_token = results.get("nextPageToken", None)

      if page_token is None:
        break

    returnedIds = [file['id'] for file in results.get("files", [])]
    response = self.list_folders(returnedIds) or []
    return response + returnedIds


  def list_drive_files(self, folder_id:str=''):
    if not folder_id: return
    folder_ids = self.list_folders([folder_id])
    folder_id_query = [f"'{folder_id}' in parents" for folder_id in folder_ids]
    query = f"({' or '.join(folder_id_query)}) and mimeType != 'application/vnd.google-apps.folder'"

    try:
      page_token = None
      while True:
        results = self.service.files().list(
          q=query,
          pageSize=10,
          fields="nextPageToken, files(id, name, modifiedTime, mimeType)",
          pageToken=page_token
        ).execute()
        page_token = results.get("nextPageToken", None)

        if page_token is None:
          break

    except HttpError as error:
      print(f"An error occurred: {error}")
      results = None

    return results
