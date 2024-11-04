from flask import Blueprint, send_file, request, jsonify
import requests
import os
import random
from flask_cors import cross_origin

# 确保 temp 目录存在
TEMP_DIR = os.path.join(os.path.dirname(__file__), 'temp')
os.makedirs(TEMP_DIR, exist_ok=True)

def file_download_route(app):
    @app.route('/all-download', methods=['GET'])
    @cross_origin()  # 允许跨域请求
    def download_file_info():
        file_url = request.args.get('url')

        if not file_url:
            return jsonify({"error": "缺少 URL 参数"}), 400

        try:
            # 使用 requests 下载文件
            response = requests.get(file_url, stream=True)
            response.raise_for_status()  # 检查请求是否成功

            # 获取文件名
            filename = os.path.basename(file_url)

            # 创建临时文件路径
            temp_file_path = os.path.join(TEMP_DIR, filename)

            # 将文件写入临时路径
            with open(temp_file_path, 'wb') as temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)

            # 生成随机数字
            random_number = random.randint(100000, 999999)

            # 返回下载链接和随机数字
            return jsonify({
                'download_url': f'/all-download/{filename}?random_number={random_number}',  # 包含随机数字的下载链接
                'random_number': random_number  # 返回的随机数字
            })

        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"请求错误: {str(e)}"}), 500
        except Exception as e:
            return jsonify({"error": f"内部服务器错误: {str(e)}"}), 500

    @app.route('/all-download/<filename>', methods=['GET'])
    @cross_origin()  # 允许跨域请求
    def download_file(filename):
        random_number = request.args.get('random_number')

        # 验证随机数字
        if not random_number or not random_number.isdigit():
            return jsonify({"error": "缺少或无效的随机数字"}), 400

        # 创建临时文件路径
        temp_file_path = os.path.join(TEMP_DIR, filename)

        if not os.path.exists(temp_file_path):
            return jsonify({"error": "文件不存在"}), 404

        # 返回文件并在关闭响应时删除文件
        response = send_file(temp_file_path, as_attachment=True, download_name=filename)
        response.call_on_close(lambda: os.remove(temp_file_path))  # 删除文件
        return response
