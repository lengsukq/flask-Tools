from flask import request, Response
import requests
from utils.request import make_response
def video_route(app):
    def get_video_content(video_url):
        try:
            response = requests.get(video_url, stream=True)
            response.raise_for_status()
            return response.content, response.headers
        except requests.RequestException as e:
            return None, str(e)

    @app.route('/video', methods=['GET'])
    def video_route_handler():
        video_url = request.args.get('url')
        if not video_url:
            return make_response('Missing video URL', 400)

        content, headers = get_video_content(video_url)
        if content is None:
            return make_response('Failed to fetch video', 500, body={'details': headers})

        # 设置响应标头
        response = Response(content, content_type='video/mp4')
        response.headers['Cache-Control'] = 'max-age=31536000, must-revalidate'
        response.headers['Content-Length'] = str(len(content))

        return response