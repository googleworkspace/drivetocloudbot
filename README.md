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

This project creates an App Engine to operate periodically to check a Google Drive Folder and move content to Google Cloud storage for a Search and Conversation Chat bot to index on.

1. Create a project
2. Enable https://console.developers.google.com/apis/api/serviceusage.googleapis.com/overview?project=<ProjectId>
3. Deploy the App Engine App ```gcloud app deploy```
4. Create a Search and Conversation Configuration; Chat app.
5. Create a Datastore in the configuration for Cloud Storage. Datastore Folder should be a cloud storage bucket listed as {GOOGLE_CLOUD_PROJECT}_{BUCKET_NAME}
6. Optional: Navigate to the bot and capture the dialog flow agent id
7. Update the app.yaml environment variables with the Datastore ID, Project, Folder ID, Storage bucket unique name, Agent ID, and [Location](https://cloud.google.com/generative-ai-app-builder/docs/locations#specify_a_multi-region_for_your_data_store) ("global", "us" or "eu")
8. Grant the App Engine Serice Account the following roles:
  - roles/storage.admin
  - roles/storage.objectAdmin
  - roles/storage.objectCreator
  - roles/aiplatform.admin
9. Redeploy the App Engine App ```gcloud app deploy```
10. Deploy the cron.yaml ```gcloud app deploy cron.yaml```
11. Share the Google Drive Folder with View access to the App Engine service account
12. Launch the Initialization by navigating to the root web url provided on deployment.
