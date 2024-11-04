from flask import Blueprint, send_file, request, abort
import requests
import os
import tempfile
from flask_cors import cross_origin
from utils.request import make_response  # 假设你有这个 utils 处理响应

def file_download_route(app):
    @app.route('/all-download', methods=['GET'])
    @cross_origin()  # 允许跨域请求
    def download_file():
        file_url = request.args.get('url')

        if not file_url:
            return make_response("缺少 URL 参数", 400)

        try:
            # 使用 requests 下载文件
            response = requests.get(file_url, stream=True)
            response.raise_for_status()  # 检查请求是否成功

            # 获取文件名
            filename = os.path.basename(file_url)

            # 创建一个临时文件来保存下载的文件
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name

            # 使用 send_file 返回下载的文件
            return send_file(temp_file_path, as_attachment=True, download_name=filename)

        except requests.exceptions.RequestException as e:
            return make_response(f"请求错误: {str(e)}", 500)
        except Exception as e:
            return make_response(f"内部服务器错误: {str(e)}", 500)
