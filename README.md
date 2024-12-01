# youtub-uploader
# 🎥 Grandpa-Friendly YouTube Auto-Uploader 

## 🌟 What is This?
This is an easy-to-use automated YouTube video uploader that runs on GitHub Actions. It can upload 2 videos every day automatically!

## 🚀 Super Simple Setup (Even for Grandpa!)

### Step 1: Prepare Your Videos
- Create a `videos` folder in your repository
- Create a `content.csv` file in the `videos` folder
- The CSV should look like this:
  ```csv
  video_path,title,description
  path/to/video1.mp4,My First Video,Description of video 1
  path/to/video2.mp4,My Second Video,Description of video 2
  ```

### Step 2: Set Up YouTube API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials
5. Download the credentials JSON file

### Step 3: Secure Your Credentials
- Encrypt your credentials file:
  ```bash
  openssl enc -aes-256-cbc -salt -in credentials.json -out credentials.json.enc
  ```
- Add the encryption passphrase to GitHub Secrets as `CREDENTIALS_PASSPHRASE`

### Step 4: Upload Credentials
- Commit `credentials.json.enc` to your repository
- Add `credentials.json` to `.gitignore`

## 🛠 Features
- Automatically upload 2 random videos daily
- Configurable upload schedule
- Supports private/public/unlisted videos
- Secure credential management

## 🔧 Customization
- Edit the cron schedule in `.github/workflows/upload_videos.yml`
- Modify upload settings in `src/uploader.py`

## 📋 Requirements
- GitHub Account
- YouTube Channel
- Google Cloud Project

## 🆘 Troubleshooting
- Check GitHub Actions logs for any upload errors
- Ensure your `content.csv` is correctly formatted
- Verify API credentials are valid

## 📜 License
[Your Preferred Open Source License]

## 🤝 Contributing
Pull requests are welcome! Please read the contribution guidelines first.
