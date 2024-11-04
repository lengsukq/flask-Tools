from flask import Flask, jsonify
from flask_cors import CORS  # 导入 flask-cors
from routes.webhook import webhook_route
from routes.time import time_route
from routes.LoveLetter import loveletter_route
from routes.markdown_route import markdown_route  # 导入新的路由
from routes.command_executor import command_executor_route  # 导入新的命令行执行路由
from routes.file_download import file_download_route  # 导入文件下载路由
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app)  # 配置 CORS

# 注册各个路由
webhook_route(app)
time_route(app)
loveletter_route(app)
markdown_route(app)  # 注册新的路由
command_executor_route(app)  # 注册新的命令行执行路由
file_download_route(app)

# 创建一个新的路由，用于显示所有路由的列表
@app.route('/', methods=['GET'])
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'url': str(rule)
        })
    return jsonify(routes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
