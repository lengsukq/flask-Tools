from flask import Flask, jsonify
from routes.webhook import webhook_route
from routes.time import time_route
from routes.LoveLetter import loveletter_route
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 注册 webhook 路由
webhook_route(app)
time_route(app)
loveletter_route(app)
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