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

Drive watch of set Folder for delta changes.
"""

import datetime
from dateutil import tz

from driveservice import Drive
from storageservice import Storage
from datastore import Datastore
from discoveryengine import DiscoveryEngine


class DriveWatch:
  """Manages the Cron Job watching for Folder Activity."""
  def __init__(self):
    self.storage = Storage()
    self.drive = Drive()
    self.datastore = Datastore()
    self.discovery = DiscoveryEngine()

  def check_files(self, folder_id, bucket_name):
    response = self.drive.list_drive_files(folder_id)
    if not response:
      return
    files = response.get("files", [])
    if not files:
      return
    stored_files = self.storage.list_bucket_files(bucket_name=bucket_name)
    # Get last update time.
    last_update =self.datastore.fetch("last_update")

    files_modified=False
    for file in files:
      # TODO: Remove the filename from the StorageList
      filename = f"{file['id']}.pdf"
      if filename in stored_files:
        stored_files.remove(filename)

      # Check if modified time is greater than last update.
      last_modified = datetime.datetime.strptime(file["modifiedTime"],
                                        '%Y-%m-%dT%H:%M:%S.%fZ').astimezone(tz = tz.tzlocal())
      last_update = last_update.astimezone(tz = tz.tzlocal())

      if not last_update or (int(last_modified.strftime('%Y%m%d%H%M%S'))
                             > int(last_update.strftime('%Y%m%d%H%M%S'))
                            ):
        # Upload file to bucket.
        self.storage.upload_file(bucket_name=bucket_name,
                                 file_id=file["id"],
                                 mime_type=file["mimeType"])
        files_modified=True
    files_deleted = False
    for stored_file in stored_files:
      self.storage.delete_blob(bucket_name=bucket_name, blob_name=stored_file)
      files_deleted = True


    if files_modified or files_deleted:
      print("Files modified.")
      self.discovery.updateCorpus()
    else:
      print("No files modified.")

    # Update last update time.
    self.datastore.store(key="last_update",
                         value=datetime.datetime.now(tz = tz.tzlocal()))

