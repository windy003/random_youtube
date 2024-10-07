from flask import Flask, request, jsonify,render_template
import requests,random
import os

# YouTube Data API key
API_KEY = "AIzaSyDuzxutoocl94tIzUNBxPQxxwg5foqDMaw"  # 请确保你设置了环境变量或直接在这里输入 API 密钥


def get_channel_id(channel_name):
    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&q={channel_name}&type=channel&key={API_KEY}'
    response = requests.get(url).json()

    if 'items' in response and len(response['items']) > 0:
        return response['items'][0]['snippet']['channelId']  # 获取频道ID
    return None



def fetch_videos_from_youtube_api(channel_id):

        # 获取频道 ID
    search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&type=video&maxResults=10000&order=date&key={API_KEY}"
    response = requests.get(search_url)
    
    if response.status_code != 200:
        print(f"请求失败，状态码：{response.status_code}")
        return {"error": "无法获取数据，请检查 API 或频道名称"}

    videos_data = response.json()
    #print(f"获取的视频数据：{videos_data}")  # 打印返回的数据

    videos = []

    # 遍历获取到的视频
    for video in videos_data.get('items', []):
        video_id = video['id']['videoId']
        video_url = f"https://www.googleapis.com/youtube/v3/videos?part=contentDetails,snippet&id={video_id}&key={API_KEY}"
        video_response = requests.get(video_url)
        if video_response.status_code == 200:
            video_info = video_response.json()
            #print(f"视频信息：{video_info}")  # 打印每个视频的信息
            videos.append(video_info['items'][0])  # 添加视频详细信息
        else:
            print(f"无法获取视频 {video_id} 的详细信息，状态码：{video_response.status_code}")


    print(videos)
    
    return videos
    

app = Flask(__name__)

def convert_duration_to_minutes(duration):
    # 初始化小时、分钟和秒
    hours = minutes = seconds = 0
    
    # 检查时长字符串中是否包含小时、分钟或秒，并提取相应的值
    if 'H' in duration:
        hours = int(duration.split('H')[0].replace('PT', ''))
        duration = duration.split('H')[1]  # 去掉小时部分，继续处理分钟和秒

    if 'M' in duration:
        minutes = int(duration.split('M')[0].replace('PT', ''))
        duration = duration.split('M')[1] if 'M' in duration else duration  # 去掉分钟部分

    if 'S' in duration:
        seconds = int(duration.split('S')[0].replace('PT', ''))

    # 计算总的分钟数
    total_minutes = hours * 60 + minutes + seconds / 60
    return total_minutes

@app.route('/get_videos', methods=['POST'])
def get_videos():
    channel_name = request.form.get('channel_name')
    min_duration = float(request.form.get('min_duration')) 
    max_duration = float(request.form.get('max_duration')) 
    
    # 获取频道ID
    channel_id = get_channel_id(channel_name)
    if not channel_id:
        return jsonify({'error': 'Channel_ID not found'})
    
    
    # 替换为实际的 API 调用以从 YouTube API 获取视频
    videos = fetch_videos_from_youtube_api(channel_id)  # 该函数应返回视频列表

    filtered_videos = []
    for video in videos:
        video_duration = video['contentDetails']['duration']
        print(video_duration)
        duration_in_minutes = convert_duration_to_minutes(video_duration)
        print(duration_in_minutes)
        if min_duration <= duration_in_minutes <= max_duration:
            filtered_videos.append(video)

    if not filtered_videos: 
        return jsonify({'error': '未找到符合指定时长范围的视频。'})
        
    random_videos = random.sample(filtered_videos, 10)

    return jsonify(random_videos)
    
    
# 首页路由，渲染输入页面
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
