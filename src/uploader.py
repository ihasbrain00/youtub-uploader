import os
import csv
import random
import json
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

class YouTubeUploader:
    def __init__(self, credentials_path, uploaded_log_path='uploaded_videos.json'):
        """
        Initialize the YouTube uploader with credentials and tracking
        
        :param credentials_path: Path to the OAuth 2.0 credentials file
        :param uploaded_log_path: Path to log of previously uploaded videos
        """
        # Load credentials from the specified path
        self.credentials = Credentials.from_authorized_user_file(credentials_path)
        
        # Build YouTube API client
        self.youtube = googleapiclient.discovery.build(
            "youtube", "v3", credentials=self.credentials
        )
        
        # Track uploaded videos
        self.uploaded_log_path = uploaded_log_path
        self.uploaded_videos = self._load_uploaded_videos()

    def _load_uploaded_videos(self):
        """
        Load the list of previously uploaded video paths
        
        :return: Set of uploaded video paths
        """
        try:
            with open(self.uploaded_log_path, 'r') as f:
                return set(json.load(f))
        except FileNotFoundError:
            return set()

    def _save_uploaded_videos(self, video_path):
        """
        Save the newly uploaded video path to the log
        
        :param video_path: Path of the uploaded video
        """
        self.uploaded_videos.add(video_path)
        
        with open(self.uploaded_log_path, 'w') as f:
            json.dump(list(self.uploaded_videos), f)

    def upload_video(self, video_path, title, description, category_id='22', privacy_status='private'):
        """
        Upload a video to YouTube, avoiding duplicates
        
        :param video_path: Path to the video file
        :param title: Title of the video
        :param description: Description of the video
        :param category_id: YouTube video category ID (default: 22 for People & Blogs)
        :param privacy_status: Video privacy status (public/private/unlisted)
        :return: Video upload response
        """
        # Check if video has already been uploaded
        if video_path in self.uploaded_videos:
            print(f"Video {video_path} has already been uploaded. Skipping.")
            return None

        try:
            # Prepare the video upload request body
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

            # Create a MediaFileUpload object
            media = MediaFileUpload(
                video_path, 
                resumable=True, 
                chunksize=1024*1024  # 1 MB chunks for better upload reliability
            )

            # Execute the upload request
            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )

            response = request.execute()
            print(f"Video uploaded successfully: {response['id']}")
            
            # Log the uploaded video
            self._save_uploaded_videos(video_path)
            
            return response

        except googleapiclient.errors.HttpError as error:
            print(f"An error occurred: {error}")
            return None

def select_videos_to_upload():
    """
    Read the content.csv file and select videos to upload
    
    :return: List of video details to upload
    """
    videos_to_upload = []
    
    # Read the list of uploaded videos to filter out duplicates
    try:
        with open('uploaded_videos.json', 'r') as f:
            uploaded_videos = set(json.load(f))
    except FileNotFoundError:
        uploaded_videos = set()
    
    with open('videos/content.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        all_videos = list(reader)
        
        # Filter out already uploaded videos
        available_videos = [
            video for video in all_videos 
            if video['video_path'] not in uploaded_videos
        ]
        
        # Randomly select 2 unique videos (or less if not enough available)
        selected_videos = random.sample(
            available_videos, 
            min(2, len(available_videos))
        )
        
        for video in selected_videos:
            videos_to_upload.append({
                'path': video['video_path'],
                'title': video['title'],
                'description': video['description']
            })
    
    return videos_to_upload

def main():
    # Path to your OAuth 2.0 credentials file (changed to 'credential.json')
    CREDENTIALS_FILE = 'credential.json'
    
    # Initialize the uploader
    uploader = YouTubeUploader(CREDENTIALS_FILE)
    
    # Select videos to upload
    videos = select_videos_to_upload()
    
    # Upload each selected video
    for video in videos:
        uploader.upload_video(
            video_path=video['path'],
            title=video['title'],
            description=video['description']
        )

if __name__ == '__main__':
    main()
