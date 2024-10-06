from flask import Flask, render_template, request, jsonify
import requests
import random

app = Flask(__name__)

# YouTube API key
API_KEY = 'AIzaSyDuzxutoocl94tIzUNBxPQxxwg5foqDMaw'

# 通过频道名称搜索频道ID
def get_channel_id(channel_name):
    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&q={channel_name}&type=channel&key={API_KEY}'
    response = requests.get(url).json()

    if 'items' in response and len(response['items']) > 0:
        return response['items'][0]['snippet']['channelId']  # 获取频道ID
    return None

# 获取随机视频列表的函数
def get_random_videos(channel_id):
    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&maxResults=50&order=date&type=video&key={API_KEY}'
    response = requests.get(url).json()
    if 'items' not in response:
        return []
    
    videos = response['items']
    random_videos = random.sample(videos, min(10, len(videos)))  # 随机选择10个视频
    video_ids = ','.join([video['id']['videoId'] for video in random_videos])

    # 获取视频的详细信息
    video_details_url = f'https://www.googleapis.com/youtube/v3/videos?part=contentDetails,snippet&id={video_ids}&key={API_KEY}'
    details_response = requests.get(video_details_url).json()

    return details_response['items']

# 首页路由，渲染输入页面
@app.route('/')
def index():
    return render_template('index.html')

# 处理视频请求的API路由
@app.route('/get_videos', methods=['POST'])
def get_videos():
    channel_name = request.form.get('channel_name')

    # 获取频道ID
    channel_id = get_channel_id(channel_name)
    if not channel_id:
        return jsonify({'error': 'Channel not found'})

    # 获取随机视频
    videos = get_random_videos(channel_id)
    
    return jsonify(videos)

if __name__ == '__main__':
    app.run(debug=True)
