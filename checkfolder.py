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

Drive watch initializer service.
"""

import os

from drivewatch import DriveWatch

def trigger_drive_watch():
  DriveWatch().check_files(folder_id=os.environ.get('FOLDER_ID'), bucket_name=f"{os.environ.get('PROJECT')}_{os.environ.get('BUCKET_NAME')}")
  return 'Triggered Drive Watch'

if __name__ == '__main__':
  trigger_drive_watch()
