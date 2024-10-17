from flask import request, Response, send_from_directory, jsonify
import subprocess
import threading
import os
import shutil
from datetime import datetime
from utils.request import make_response

# 全局变量，用于跟踪当前是否有命令行任务在执行
current_process = None
lock = threading.Lock()
# 存储压缩文件路径
compressed_file_path = None

def stream_output(process):
    global compressed_file_path
    for line in iter(process.stdout.readline, b''):
        yield line  # 直接 yield line，不需要 decode
    process.stdout.close()
    process.wait()
    current_directory = os.getcwd()
    yield f"\n当前目录: {current_directory}\n"
    # 检查是否有 dist 文件夹，并压缩
    if os.path.exists('dist'):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        zip_filename = f'dist_{timestamp}.zip'
        shutil.make_archive(zip_filename.replace('.zip', ''), 'zip', 'dist')
        compressed_file_path = os.path.join(current_directory, zip_filename)
        yield f"\nDist 文件夹已压缩为 {zip_filename}\n"
        yield f"\n下载链接: /download/{zip_filename}\n"
    else:
        yield "\n未找到 dist 文件夹\n"

def command_executor_route(app):
    @app.route('/execute', methods=['POST'])
    def execute():
        global current_process, compressed_file_path

        with lock:
            if current_process is not None and current_process.poll() is None:
                # 如果当前有任务在执行，返回错误信息
                return make_response("命令已在运行", 200)

            # 获取命令行参数
            command = request.json.get('command')
            if not command:
                return make_response("未提供命令", 200)

            # 获取环境变量 AUTO_BUILD_SHELL_PATH 的值
            auto_build_shell_path = os.getenv('AUTO_BUILD_SHELL_PATH')
            if not auto_build_shell_path:
                return make_response("环境变量 AUTO_BUILD_SHELL_PATH 未设置", 200)

            # 切换到 AUTO_BUILD_SHELL_PATH 目录
            try:
                os.chdir(auto_build_shell_path)
            except FileNotFoundError:
                return make_response(f"目录 {auto_build_shell_path} 不存在", 200)

            # 启动命令行任务
            try:
                current_process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
            except Exception as e:
                return make_response(f"错误: 执行 '{command}' 失败。异常: {str(e)}", 200)

        # 实时输出命令行结果
        return Response(stream_output(current_process), mimetype='text/plain')

    @app.route('/download/<filename>', methods=['GET'])
    def download(filename):
        global compressed_file_path
        if compressed_file_path and os.path.exists(compressed_file_path):
            return send_from_directory(os.path.dirname(compressed_file_path), os.path.basename(compressed_file_path), as_attachment=True)
        else:
            return make_response("文件未找到", 200)