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

Initialization of APIs.
"""

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

class ApiEnable:

  def __init__(self):
    self.creds = GoogleCredentials.get_application_default()
    self.serviceusage = discovery.build("serviceusage", "v1", credentials=self.creds)
    self.crm = discovery.build("cloudresourcemanager", "v1", credentials=self.creds)
    self.iam = discovery.build("iam", "v1", credentials=self.creds)


  def enable_api(self, project_id, api):
      """Enables the GCP service APIs

      Args:
          project_id : The ID of the project where the service status is being checked
      """

      # Get the API service status in the project
      api_status = self._get_service_api_status(
          api, project_id
      )

      # Enable the API service in the project
      if api_status != "ENABLED":
          self.serviceusage.services().enable(
              name=f"projects/{project_id}/services/{api}"
          ).execute()

          print(f"Enabled {api} API in project : {project_id}")


  def _get_service_api_status(self, api_name, project_id):
      """
      Get the current status of a GCP service API

      Args:
          api_name : API name whose status is to be returned
          project_id : The ID of the project where the service status is being checked

      Returns:
          string : service api status
      """
      response = (
          self.serviceusage.services()
          .get(name=f"projects/{project_id}/services/{api_name}")
          .execute()
      )
      return response["state"]

