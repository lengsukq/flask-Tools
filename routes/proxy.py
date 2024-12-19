from flask import jsonify,request
import requests

# 定义一个通用的代理请求函数
def proxy_request(target_url, method, headers=None, data=None):
    try:
        # 发送请求到目标 URL
        response = requests.request(
            method=method,
            url=target_url,
            headers=headers,
            data=data,
            timeout=10
        )
        # 返回目标 URL 的响应内容、状态码和响应头
        return response.content, response.status_code, response.headers.items()
    except requests.exceptions.RequestException as e:
        # 捕获请求异常并返回错误信息
        return jsonify({'error': str(e)}), 500, {}

# 定义代理路由
def proxy_route(app):
    @app.route('/proxy', methods=['GET', 'POST'])
    def proxy():
        # 获取目标 URL
        target_url = request.args.get('url')
        if not target_url:
            return jsonify({'error': 'Missing URL parameter'}), 400

        # 获取请求方法
        method = request.method

        # 获取请求头（移除 Flask 自动添加的 Host 头）
        headers = dict(request.headers)
        headers.pop('Host', None)

        # 获取请求体（如果是 POST 请求）
        data = request.get_data()

        # 调用代理请求函数
        return proxy_request(target_url, method, headers, data)