from utils.request import make_response
import os
import subprocess

def webhook_route(app):
    @app.route('/webhook', methods=['GET', 'POST'])
    def webhook():
        return handle_webhook('/home/code/vitePress-Web', 'yarn docs:build')

    @app.route('/webhook-opt', methods=['GET', 'POST'])
    def webhook_opt():
        return handle_webhook('/home/cunchu/code/ibs-jeecg-vue', 'yarn build:test2')

    def handle_webhook(target_dir, build_command):
        try:
            # 步骤 1: 检查当前工作目录
            current_dir = os.getcwd()

            # 步骤 2: 检查目标目录是否存在
            if not os.path.exists(target_dir):
                return make_response(f"错误: 目标目录 {target_dir} 不存在", 500)
            if not os.access(target_dir, os.R_OK | os.W_OK | os.X_OK):
                return make_response(f"错误: 对目录 {target_dir} 没有足够的权限", 500)

            # 步骤 3: 改变当前工作目录
            try:
                os.chdir(target_dir)
            except Exception as e:
                return make_response(f"错误: 无法切换到目录 {target_dir}。异常: {str(e)}", 500)

            # 步骤 4: 执行 `git pull`
            try:
                git_pull_command = "git pull"
                git_pull_process = subprocess.Popen(git_pull_command, shell=True)
                git_pull_process.wait()  # 等待 git pull 完成

                # 检查 `git pull` 的返回码
                if git_pull_process.returncode != 0:
                    return make_response("git pull 过程中发生错误", 500)
            except Exception as e:
                return make_response(f"错误: 执行 'git pull' 失败。异常: {str(e)}", 500)

            # 步骤 5: 执行编译命令
            try:
                build_process = subprocess.Popen(build_command, shell=True)
                return make_response("命令已成功启动", 200)
            except Exception as e:
                return make_response(f"错误: 执行 '{build_command}' 失败。异常: {str(e)}", 500)

        except Exception as e:
            return make_response(f"一般性错误: {str(e)}", 500)