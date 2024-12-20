from flask import request, Response, send_from_directory, jsonify
import subprocess
import threading
import os
import shutil
from utils.request import make_response
import re
from datetime import datetime, timedelta
from pytz import timezone

# 全局变量，用于跟踪当前是否有命令行任务在执行
current_process = None
lock = threading.Lock()
# 存储压缩文件路径
compressed_file_path = None

# 从环境变量中获取 ZIP 文件存储路径，如果没有定义，使用默认值 'zip_files'
zip_directory = os.getenv('ZIP_DIRECTORY_PATH', 'zip_files')

def sanitize_filename(filename):
    # 替换非法字符为下划线
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return sanitized

def stream_output(process, env_cus_path, api_base_url, selected_branch):
    global compressed_file_path
    try:
        while True:
            line = process.stdout.readline()
            if not line:
                break
            yield line

        process.stdout.close()
        process.wait()

        # 检查是否有 dist 文件夹，并压缩
        current_directory = os.getcwd()
        yield f"\n当前目录: {current_directory}\n"

        if os.path.exists('dist'):
            # 确保 ZIP 文件目录存在
            if not os.path.exists(zip_directory):
                os.makedirs(zip_directory)

            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            # 去除 http 或 https 前缀
            sanitized_api_base_url = re.sub(r'^https?://', '', api_base_url)
            # 生成压缩文件名
            sanitized_api_base_url = sanitize_filename(sanitized_api_base_url)
            zip_filename = f'{timestamp}_{sanitized_api_base_url}_{selected_branch}.zip'
            zip_path = os.path.join(zip_directory, zip_filename)
            shutil.make_archive(zip_path.replace('.zip', ''), 'zip', 'dist')
            compressed_file_path = zip_path
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
                command = 'nvm use 16 && yarn vue-cli-service build --mode cus'

                # 检查必传参数
                if not selected_branch or not api_base_url or not web_base_url or not cas_base_url or not online_base_url:
                    return make_response("未提供必填项", 200)
            else:
                # 检查必传参数
                if not selected_branch:
                    return make_response("未提供必填项", 200)

            # 检查命令是否以 'yarn' 或 'vue-cli-service' 开头
            if not command.startswith('nvm') and not command.startswith('vue-cli-service'):
                return make_response({"命令必须是 'nvm' 或 'vue-cli-service' 开头"}, 200)

            # 获取环境变量 AUTO_BUILD_SHELL_PATH 的值
            auto_build_shell_path = os.getenv('AUTO_BUILD_SHELL_PATH')
            if not auto_build_shell_path:
                return make_response("环境变量 AUTO_BUILD_SHELL_PATH 未设置", 200)

            # 切换到 AUTO_BUILD_SHELL_PATH 目录
            try:
                os.chdir(auto_build_shell_path)
            except FileNotFoundError:
                return make_response(f"目录 {auto_build_shell_path} 不存在", 200)

            # 删除现有的依赖
            if os.path.exists('node_modules'):
                shutil.rmtree('node_modules')  # 删除 node_modules 文件夹

            if os.path.exists('yarn.lock'):
                os.remove('yarn.lock')  # 删除 yarn.lock 文件

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

            # 修改命令以加载 nvm 环境
            full_command_with_nvm = f"source $HOME/.nvm/nvm.sh && {full_command}"

            # 启动命令行任务
            try:
                current_process = subprocess.Popen(
                    full_command_with_nvm,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    executable='/bin/bash'  # 确保使用 bash 来加载 nvm
                )
            except Exception as e:
                return make_response(f"错误: 执行 '{command}' 失败。异常: {str(e)}", 200)

        timeout = 360
        timer = threading.Timer(timeout, current_process.kill)
        timer.start()

        response = Response(stream_output(current_process, env_cus_path, api_base_url, selected_branch), mimetype='text/plain')

        timer.cancel()

        return response

    @app.route('/download/<filename>', methods=['GET'])
    def download(filename):
        file_path = os.path.join(zip_directory, filename)
        if os.path.exists(file_path):
            return send_from_directory(zip_directory, filename, as_attachment=True)
        else:
            return make_response("文件未找到", 200)

    @app.route('/list-zips', methods=['POST'])
    def list_zips():
        if not os.path.exists(zip_directory):
            return make_response("没有找到任何压缩文件", 200)

        # 获取分页参数
        page = int(request.json.get('page', 1))
        per_page = int(request.json.get('per_page', 10))

        zip_files = [f for f in os.listdir(zip_directory) if f.endswith('.zip')]
        total_files = len(zip_files)

        # 计算分页
        start = (page - 1) * per_page
        end = start + per_page
        paginated_files = zip_files[start:end]

        zip_links = [{'filename': f, 'download_link': f'/download/{f}'} for f in paginated_files]

        # 返回分页结果
        return make_response("获取成功", 200, {
            'total_files': total_files,
            'page': page,
            'per_page': per_page,
            'files': zip_links
        })

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

    # 定义项目与环境变量的映射关系
    REPO_ENV_MAP = {
        'ibs-jeecg-vue': 'IBS_JEECG_VUE_PATH',
        'epic-designer-xf': 'EPIC_DESIGNER_XF_PATH',
        'vitepress-xf': 'VITEPRESS_XF_PATH',
    }

    @app.route('/git-commits', methods=['GET'])
    def git_commits():
        # 获取项目参数，默认为 "ibs-jeecg-vue"
        repo = request.args.get('repo', 'ibs-jeecg-vue')

        # 检查项目是否在映射中
        if repo not in REPO_ENV_MAP:
            return make_response(f"无效的项目: {repo}，请使用以下项目之一: {', '.join(REPO_ENV_MAP.keys())}", 400)

        # 获取对应的环境变量名称
        env_var_name = REPO_ENV_MAP[repo]

        # 从环境变量中获取项目路径
        repo_path = os.getenv(env_var_name)
        if not repo_path:
            return make_response(f"环境变量 {env_var_name} 未设置，请设置对应的项目路径", 400)

        # 切换到对应的项目目录
        try:
            os.chdir(repo_path)
        except FileNotFoundError:
            return make_response(f"目录 {repo_path} 不存在", 500)

        # 获取日期范围参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # 检查日期参数是否有效
        if not start_date or not end_date:
            return make_response("无效的日期范围，请提供 start_date 和 end_date 参数", 400)

        try:
            # 尝试将日期字符串转换为 datetime 对象
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # 将结束日期加一天
        except ValueError:
            return make_response("日期格式无效，请使用 YYYY-MM-DD 格式", 400)

        # 假设服务器时区是 'Asia/Shanghai'
        server_timezone = timezone('Asia/Shanghai')

        # 将 start_date 和 end_date 转换为 UTC 时间
        start_date_utc = server_timezone.localize(start_date).astimezone(timezone('UTC'))
        end_date_utc = server_timezone.localize(end_date).astimezone(timezone('UTC'))

        try:
            # 拉取所有远程分支到本地
            try:
                subprocess.check_output(['git', 'fetch', '--all'], encoding='utf-8')
                print("所有远程分支已成功拉取到本地。")
            except subprocess.CalledProcessError as e:
                return make_response(f"拉取远程分支时出错: {e}", 500)

            # 获取所有分支的提交记录，并过滤时间范围
            commits = subprocess.check_output(
                [
                    'git', 'log', '--all', '--since', start_date_utc.strftime('%Y-%m-%d %H:%M:%S'),
                    '--until', end_date_utc.strftime('%Y-%m-%d %H:%M:%S'),
                    '--pretty=format:%H %an %s %ad', '--date=iso'
                ],
                encoding='utf-8'
            ).splitlines()

            # 将提交记录按作者分类
            commits_by_author = {}

            # 规范化作者名称的函数
            def normalize_author(author):
                if author == 'huangmingyu\\innover':
                    return 'huangmingyu'
                if author == 'lengsukq':
                    return 'tanghongxin'
                if author == '刘泽琼':
                    return 'liuzeqiong'
                return author

            for commit in commits:
                # 按空格分割原始数据
                parts = commit.split(maxsplit=3)
                if len(parts) < 4:
                    # 如果提交记录格式不正确，跳过该行
                    continue

                # 提取 hash（截取前 9 位）
                commit_hash = parts[0][:9]

                # 提取作者
                author = parts[1]

                # 提取 message 和 date
                message_and_date = parts[2] + ' ' + parts[3]  # 合并 message 和 date
                date_match = re.search(r'\d{4}-\d{2}-\d{2}', message_and_date)  # 查找日期
                if date_match:
                    date_start = date_match.start()
                    message = message_and_date[:date_start].strip()  # 提取 message
                    date = message_and_date[date_start:].strip()  # 提取 date
                else:
                    # 如果找不到日期，则将整个 message_and_date 作为 message
                    message = message_and_date.strip()
                    date = ''

                # 规范化作者名称
                author = normalize_author(author)

                # 如果作者不存在，创建一个新的列表
                if author not in commits_by_author:
                    commits_by_author[author] = []

                # 将提交记录添加到对应作者的列表中
                commits_by_author[author].append({
                    'hash': commit_hash,
                    'message': message,
                    'date': date
                })

            return make_response('获取成功', 200, commits_by_author)
        except Exception as e:
            return make_response(f"错误: 获取 Git 提交记录失败。异常: {str(e)}", 500)