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

Cloud Storage Service.
"""
import io

from google.cloud import storage
from driveservice import Drive
from google.cloud.storage import Blob

class Storage:
  def __init__(self):
    self.storage = storage.Client()
    self.drive = Drive()


  def check_storage(self, bucket_name: str, storage_class: str = "STANDARD"):
    """
    Check if the bucket exists and create the bucket if not.
    """
    bucket = self.storage.bucket(bucket_name)
    if(not bucket.exists()):
      bucket = self.create_bucket_class_location(bucket_name, storage_class)
    return bucket


  def create_bucket_class_location(self, bucket_name: str, storage_class: str = "STANDARD"):
    """
    Create a new bucket in the US region with the coldline storage
    class
    """
    # bucket_name = "your-new-bucket-name"

    bucket = self.storage.bucket(bucket_name)
    bucket.storage_class = storage_class
    new_bucket = self.storage.create_bucket(bucket, location="us")
    new_bucket.iam_configuration.uniform_bucket_level_access_enabled = True
    new_bucket.patch()

    print(
        "Created bucket {} in {} with storage class {}".format(
            new_bucket.name, new_bucket.location, new_bucket.storage_class
        )
    )
    return new_bucket

  def list_bucket_files(self, bucket_name: str):
    blobs = self.storage.list_blobs(bucket_name)
    return [blob.name for blob in blobs]

  def upload_file(self, bucket_name: str, file_id: str, mime_type: str):
    """
    Uploads a file to the bucket from Google Drive.
    """
    file = self.drive.get_drive_blob(file_id, mime_type)
    bucket = self.storage.bucket(bucket_name)
    blob = Blob(f"{file_id}.pdf", bucket)
    stream = io.BytesIO(file)
    blob.upload_from_file(stream, rewind=True)

    print(
        "File {} uploaded to {}.".format(
            blob.name, bucket.name
        )
    )

  def delete_blob(self, bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"

    bucket = self.storage.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    generation_match_precondition = None

    # Optional: set a generation-match precondition to avoid potential race conditions
    # and data corruptions. The request to delete is aborted if the object's
    # generation number does not match your precondition.
    blob.reload()  # Fetch blob metadata to use in generation_match_precondition.
    generation_match_precondition = blob.generation

    blob.delete(if_generation_match=generation_match_precondition)

    print(f"Blob {blob_name} deleted.")
