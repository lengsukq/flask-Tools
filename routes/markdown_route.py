from flask import request, jsonify
from datetime import datetime
import os
from utils.request import make_response
def markdown_route(app):
    @app.route('/save-markdown', methods=['POST'])
    def save_markdown():
        try:
            # 获取请求中的 Markdown 内容和作者信息
            markdown_content = request.json.get('content')
            author = request.json.get('author')
            path_array = request.json.get('path')  # 获取路径参数数组

            if not markdown_content:
                return make_response('未提供内容', 400)

            if not author:
                return make_response('未提供作者信息', 400)

            if not path_array or not isinstance(path_array, list):
                return make_response('未提供路径信息或路径信息格式不正确', 400)

            # 在内容尾部添加作者信息
            markdown_content = f"{markdown_content}\n\n---\n\n# 作者: {author}"

            # 获取环境变量 MD_SAVE_PATH_ROOT
            md_save_path_root = os.getenv('MD_SAVE_PATH_ROOT')
            if not md_save_path_root:
                return make_response('环境变量 MD_SAVE_PATH_ROOT 未设置', 500)

            # 拼接路径数组
            path = os.path.join(md_save_path_root, *path_array)

            # 指定保存文件的路径
            save_directory = path
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)

            # 获取路径下已有的 Markdown 文件数量
            existing_md_files = [f for f in os.listdir(save_directory) if f.endswith('.md')]
            file_count = len(existing_md_files) + 1

            # 生成文件名，格式为 序号.作者_年月日时分.md
            now = datetime.now()
            filename = f"{file_count}.{author}_{now.strftime('%Y%m%d%H%M')}.md"

            # 保存 Markdown 文件，指定编码为 utf-8
            file_path = os.path.join(save_directory, filename)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(markdown_content)

            return make_response('Markdown 文件保存成功', 200, {'filename': file_path})
        except Exception as e:
            return make_response(f'保存 Markdown 文件时出错: {str(e)}', 500)

    @app.route('/get-markdown-files', methods=['GET'])
    def get_markdown_files():
        try:
            # 获取环境变量 MD_SAVE_PATH_ROOT
            md_save_path_root = os.getenv('MD_SAVE_PATH_ROOT')
            if not md_save_path_root:
                return make_response('环境变量 MD_SAVE_PATH_ROOT 未设置', 400)

            # 检查路径是否存在
            if not os.path.exists(md_save_path_root):
                return make_response('路径不存在', 400)

            # 获取请求参数 type
            file_type = request.args.get('type', 'folder')

            # 忽略的文件夹列表
            ignored_folders = {'conf', 'data', '.vitepress', 'request', 'temp', 'components'}

            # 递归获取文件夹和 .md 文件
            def get_files_and_folders(path, is_root=False):
                items = []
                for entry in os.listdir(path):
                    full_path = os.path.join(path, entry)
                    if os.path.isdir(full_path):
                        if entry in ignored_folders:
                            continue  # 跳过忽略的文件夹
                        items.append({'type': 'folder', 'name': entry, 'children': get_files_and_folders(full_path)})
                    elif os.path.isfile(full_path) and entry.endswith('.md'):
                        if file_type == 'all' or not is_root:  # 当 type=all 时，包括根目录下的文件
                            items.append({'type': 'file', 'name': entry})
                return items

            files_and_folders = get_files_and_folders(md_save_path_root, is_root=True)

            # 如果 type=folder，只返回 type 为 folder 的数据
            if file_type == 'folder':
                def filter_folders(items):
                    filtered_items = []
                    for item in items:
                        if item['type'] == 'folder':
                            item['children'] = filter_folders(item['children'])
                            filtered_items.append(item)
                    return filtered_items

                files_and_folders = filter_folders(files_and_folders)

            return make_response('获取目录成功', 200, files_and_folders)
        except Exception as e:
            return make_response(f'获取 Markdown 文件时出错: {str(e)}', 500)