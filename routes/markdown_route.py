
from flask import request
import time
import os
from utils.request import make_response

def markdown_route(app):
    @app.route('/save-markdown', methods=['POST'])
    def save_markdown():
        try:
            # 获取请求中的 Markdown 内容和作者信息
            markdown_content = request.json.get('content')
            author = request.json.get('author')

            if not markdown_content:
                return make_response('No content provided', 400)

            if not author:
                return make_response('No author provided', 400)

            # 在 content 开头添加作者信息
            markdown_content = f"# Author: {author}\n\n{markdown_content}"

            # 生成文件名
            filename = f"output_{int(time.time())}.md"

            # 指定保存文件的路径
            save_directory = os.path.join(app.root_path, 'markdown_files')
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)

            # 保存 Markdown 文件，指定编码为 utf-8
            file_path = os.path.join(save_directory, filename)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(markdown_content)

            return make_response('Markdown file saved successfully', 200, {'filename': file_path})
        except Exception as e:
            return make_response(f'Error saving markdown file: {str(e)}', 500)