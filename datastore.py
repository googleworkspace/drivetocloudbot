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

Datastore service.
"""


from google.cloud import datastore

class Datastore:
  """Datastore class."""

  def __init__(self):
      self.client = datastore.Client()

  def store(self, key, value, table="settings"):
    entity = datastore.Entity(key=self.client.key(table, "drive"))
    obj={}
    obj[key]=value
    entity.update(obj)
    res = self.client.put(entity)

  def fetch(self, prop, table="settings"):
    key = self.client.key(table, "drive")
    result = self.client.get(key)
    if result is None:
      return None
    return result.get(prop)
