from flask import request, Response, send_from_directory
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

def stream_output(process, env_cus_path):
    global compressed_file_path
    try:
        while True:
            line = process.stdout.readline()
            if not line:
                break
            yield line  # 直接 yield line，不需要 decode

        process.stdout.close()
        process.wait()

        # 检查是否有 dist 文件夹，并压缩
        current_directory = os.getcwd()
        yield f"\n当前目录: {current_directory}\n"

        if os.path.exists('dist'):
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            zip_filename = f'dist_{timestamp}.zip'
            shutil.make_archive(zip_filename.replace('.zip', ''), 'zip', 'dist')
            compressed_file_path = os.path.join(current_directory, zip_filename)
            yield f"\nDist 文件夹已压缩为 {zip_filename}\n"
            yield f"\n下载链接: /download/{zip_filename}\n"
        else:
            yield "\n未找到 dist 文件夹\n"

        # 删除 .env.cus 文件
        if os.path.exists(env_cus_path):
            os.remove(env_cus_path)
            yield "\n.env.cus 文件已删除\n"

    except Exception as e:
        yield f"\n错误: {str(e)}\n"

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
            selected_branch = request.json.get('selectedBranch')
            api_base_url = request.json.get('apiBaseUrl')
            web_base_url = request.json.get('webBaseUrl')
            cas_base_url = request.json.get('casBaseUrl')
            online_base_url = request.json.get('onlineBaseUrl')

            # 如果没有传命令，则默认执行 vue-cli-service serve --mode cus
            if not command:
                command = 'vue-cli-service serve --mode cus'

                # 检查必传参数
                if not selected_branch or not api_base_url or not web_base_url or not cas_base_url or not online_base_url:
                    return make_response("未提供必填项", 200)
            else:
                # 检查必传参数
                if not selected_branch:
                    return make_response("未提供必填项", 200)

            # 检查命令是否以 'yarn' 或 'vue-cli-service' 开头
            if not command.startswith('yarn') and not command.startswith('vue-cli-service'):
                return make_response({"命令必须是 'yarn' 或 'vue-cli-service' 开头"}, 200)

            # 获取环境变量 AUTO_BUILD_SHELL_PATH 的值
            auto_build_shell_path = os.getenv('AUTO_BUILD_SHELL_PATH')
            if not auto_build_shell_path:
                return make_response("环境变量 AUTO_BUILD_SHELL_PATH 未设置", 200)

            # 切换到 AUTO_BUILD_SHELL_PATH 目录
            try:
                os.chdir(auto_build_shell_path)
            except FileNotFoundError:
                return make_response(f"目录 {auto_build_shell_path} 不存在", 200)

            # 生成 .env.cus 文件
            env_cus_path = os.path.join(auto_build_shell_path, '.env.cus')
            with open(env_cus_path, 'w') as f:
                f.write(f"NODE_ENV=cus\n")
                f.write(f"VUE_APP_API_BASE_URL={api_base_url}\n")
                f.write(f"VUE_APP_WEB_BASE_URL={web_base_url}\n")
                f.write(f"VUE_APP_CAS_BASE_URL={cas_base_url}\n")
                f.write(f"VUE_APP_ONLINE_BASE_URL={online_base_url}\n")

            # 如果提供了 selectedBranch 参数，切换分支并执行相关操作
            if selected_branch:
                # 拼接命令
                full_command = f"git fetch origin && git checkout -f {selected_branch} && git reset --hard origin/{selected_branch} && yarn install --no-lockfile && {command}"
            else:
                full_command = f"yarn install --no-lockfile && {command}"

            # 启动命令行任务
            try:
                current_process = subprocess.Popen(
                    full_command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
            except Exception as e:
                return make_response(f"错误: 执行 '{command}' 失败。异常: {str(e)}", 200)

        # 设置超时时间（例如 60 秒）
        timeout = 360
        timer = threading.Timer(timeout, current_process.kill)
        timer.start()

        # 实时输出命令行结果
        response = Response(stream_output(current_process, env_cus_path), mimetype='text/plain')

        # 停止计时器
        timer.cancel()

        return response

    @app.route('/download/<filename>', methods=['GET'])
    def download(filename):
        global compressed_file_path
        if compressed_file_path and os.path.exists(compressed_file_path):
            return send_from_directory(os.path.dirname(compressed_file_path), os.path.basename(compressed_file_path), as_attachment=True)
        else:
            return make_response("文件未找到", 200)

    @app.route('/git-branches', methods=['GET'])
    def git_branches():
        # 获取环境变量 AUTO_BUILD_SHELL_PATH 的值
        auto_build_shell_path = os.getenv('AUTO_BUILD_SHELL_PATH')
        if not auto_build_shell_path:
            return make_response("环境变量 AUTO_BUILD_SHELL_PATH 未设置", 200)

        # 切换到 AUTO_BUILD_SHELL_PATH 目录
        try:
            os.chdir(auto_build_shell_path)
        except FileNotFoundError:
            return make_response(f"目录 {auto_build_shell_path} 不存在", 200)

        try:
            # 获取当前目录下的 Git 分支
            branches = subprocess.check_output(['git', 'branch', '-a'], text=True).splitlines()
            current_branch = [branch.strip('* ') for branch in branches if branch.startswith('*')][0]
            branches = [branch.strip() for branch in branches]
            return make_response("获取成功", 200, {
                'branches': branches,
                'current_branch': current_branch
            })
        except Exception as e:
            return make_response(f"错误: 获取 Git 分支失败。异常: {str(e)}", 200)