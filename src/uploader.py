import os
import csv
import random
import json
import logging
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('youtube_upload.log'),
        logging.StreamHandler()
    ]
)

# EMBEDDED CREDENTIALS (BE VERY CAREFUL WITH THESE!)
CLIENT_CONFIG = {
    "installed": {
        "client_id": "578799172154-ndjv3pi3d441ed4srcshd93m6jmg9us1.apps.googleusercontent.com",
        "project_id": "yt-uploader-443410",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": ["http://localhost"]
    }
}

class YouTubeUploader:
    def __init__(self, max_uploads=2, privacy_status='private'):
        """
        Initialize the YouTube uploader with advanced configuration
        
        :param max_uploads: Maximum number of videos to upload per run
        :param privacy_status: Default video privacy status
        """
        self.max_uploads = max_uploads
        self.default_privacy = privacy_status
        
        self.uploaded_videos = self._load_uploaded_videos()
        self._authenticate()

    def _authenticate(self):
        """
        Authenticate with YouTube API
        """
        try:
            # Create OAuth flow
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config(
                CLIENT_CONFIG,
                scopes=['https://www.googleapis.com/auth/youtube.upload']
            )

            # Run local server to authorize
            credentials = flow.run_local_server(port=0)

            # Build YouTube API client
            self.youtube = googleapiclient.discovery.build(
                "youtube", "v3", credentials=credentials
            )
            
            logging.info("Successfully authenticated with YouTube API")

        except Exception as e:
            logging.error(f"Authentication failed: {e}")
            raise

    def _load_uploaded_videos(self, uploaded_log_path='uploaded_videos.json'):
        """
        Load previously uploaded video log
        """
        try:
            with open(uploaded_log_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                'video_paths': [],
                'video_ids': [],
                'upload_history': []
            }

    def _save_uploaded_videos(self, video_path, video_id):
        """
        Log uploaded video details
        """
        upload_entry = {
            'video_path': video_path,
            'video_id': video_id,
            'uploaded_at': datetime.now().isoformat()
        }

        # Update log
        self.uploaded_videos['video_paths'].append(video_path)
        self.uploaded_videos['video_ids'].append(video_id)
        self.uploaded_videos['upload_history'].append(upload_entry)

        # Limit history to prevent excessive growth
        max_history = 100
        self.uploaded_videos['upload_history'] = self.uploaded_videos['upload_history'][-max_history:]

        with open('uploaded_videos.json', 'w') as f:
            json.dump(self.uploaded_videos, f, indent=2)

    def upload_video(self, video_path, title, description, 
                     category_id='22', privacy_status=None):
        """
        Upload a single video to YouTube
        """
        # Use default privacy if not specified
        privacy_status = privacy_status or self.default_privacy

        # Check if video has already been uploaded
        if video_path in self.uploaded_videos.get('video_paths', []):
            logging.warning(f"Video {video_path} already uploaded. Skipping.")
            return None

        try:
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy_status
                }
            }

            media = MediaFileUpload(
                video_path, 
                resumable=True, 
                chunksize=1024*1024  # 1 MB chunks
            )

            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )

            response = request.execute()
            video_id = response['id']

            logging.info(f"Successfully uploaded video: {video_id}")
            
            # Log the upload
            self._save_uploaded_videos(video_path, video_id)

            return response

        except googleapiclient.errors.HttpError as error:
            logging.error(f"YouTube API upload error: {error}")
        except Exception as e:
            logging.error(f"Unexpected upload error: {e}")

        return None

def select_videos_to_upload(max_videos=2):
    """
    Select videos to upload from content.csv
    """
    try:
        with open('videos/content.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            all_videos = list(reader)

            # Load previously uploaded videos to skip duplicates
            try:
                with open('uploaded_videos.json', 'r') as f:
                    uploaded_data = json.load(f)
                    uploaded_paths = uploaded_data.get('video_paths', [])
            except (FileNotFoundError, json.JSONDecodeError):
                uploaded_paths = []

            # Filter out already uploaded videos
            available_videos = [
                video for video in all_videos 
                if video['video_path'] not in uploaded_paths
            ]

            # Randomly select videos
            selected_videos = random.sample(
                available_videos, 
                min(max_videos, len(available_videos))
            )

            return selected_videos

    except Exception as e:
        logging.error(f"Error selecting videos: {e}")
        return []

def main():
    # Configuration
    MAX_UPLOADS = 2
    PRIVACY_STATUS = 'private'  # or 'public', 'unlisted'

    try:
        # Initialize uploader
        uploader = YouTubeUploader(
            max_uploads=MAX_UPLOADS,
            privacy_status=PRIVACY_STATUS
        )

        # Select videos to upload
        videos_to_upload = select_videos_to_upload(MAX_UPLOADS)

        # Upload each selected video
        for video in videos_to_upload:
            uploader.upload_video(
                video_path=video['video_path'],
                title=video['title'],
                description=video['description']
            )

    except Exception as e:
        logging.error(f"Critical error in main execution: {e}")

if __name__ == '__main__':
    main()