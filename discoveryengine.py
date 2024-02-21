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

DiscoveryEngine service.
"""

import os

from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1beta as discoveryengine_v1

class DiscoveryEngine:
  def __init__(self):
    self.client = discoveryengine_v1.DocumentServiceClient(client_options = (
        ClientOptions(api_endpoint=f"{os.environ.get('LOCATION')}-discoveryengine.googleapis.com")
        if os.environ.get('LOCATION') != "global"
        else None
    ))

  def updateCorpus(self):
    parent = self.client.branch_path(
        project=os.environ.get('PROJECT'),
        location=os.environ.get('LOCATION'),
        data_store=os.environ.get('DATASTORE_ID'),
        branch="default_branch",
    )

    request = discoveryengine_v1.ImportDocumentsRequest(
        parent=parent,
        reconciliation_mode=discoveryengine_v1.ImportDocumentsRequest.ReconciliationMode.FULL,
          gcs_source=discoveryengine_v1.GcsSource(
            input_uris=[
              f"gs://{os.environ.get('PROJECT')}_{os.environ.get('BUCKET_NAME')}/*.pdf"
            ],
            data_schema="content"
        )
    )

    operation = self.client.import_documents(request=request)

    print("Waiting for operation to complete...")

    response = operation.result()

    # Handle the response
    print(response)
