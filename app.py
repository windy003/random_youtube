from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 使用你自己的 YouTube API key
YOUTUBE_API_KEY = 'YOUR_API_KEY'

def get_videos_from_channel(channel_name):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

    # 获取频道的 ID
    channel_response = youtube.search().list(
        q=channel_name,
        type='channel',
        part='id,snippet',
        maxResults=1
    ).execute()

    if not channel_response['items']:
        return {'error': 'No channel found with that name.'}

    channel_id = channel_response['items'][0]['id']['channelId']

    # 根据频道 ID 获取视频
    video_response = youtube.search().list(
        channelId=channel_id,
        part='id,snippet',
        order='date',
        maxResults=10  # 返回前 10 个视频
    ).execute()

    videos = []
    for item in video_response['items']:
        if item['id']['kind'] == 'youtube#video':  # 过滤掉非视频的条目
            video_id = item['id']['videoId']
            video_details = youtube.videos().list(
                id=video_id,
                part='contentDetails'
            ).execute()

            # 获取视频的详情
            if video_details['items']:
                video = {
                    'id': video_id,
                    'snippet': item['snippet'],
                    'contentDetails': video_details['items'][0]['contentDetails']
                }
                videos.append(video)

    return videos

@app.route('/get_videos', methods=['POST'])
def get_videos():
    channel_name = request.form.get('channel_name')

    if not channel_name:
        return jsonify({'error': 'Channel name is required.'})

    try:
        videos = get_videos_from_channel(channel_name)
    except Exception as e:
        return jsonify({'error': str(e)})

    return jsonify(videos)

if __name__ == '__main__':
    app.run(debug=True)
