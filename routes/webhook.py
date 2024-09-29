# routes/webhook.py
from flask import request
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
            # Step 1: 检查当前工作目录
            current_dir = os.getcwd()

            # Step 2: 检查目标目录是否存在
            if not os.path.exists(target_dir):
                return f"Error: Target directory {target_dir} does not exist", 500
            if not os.access(target_dir, os.R_OK | os.W_OK | os.X_OK):
                return f"Error: No sufficient permissions for {target_dir}", 500

            # Step 3: 改变当前工作目录
            try:
                os.chdir(target_dir)
            except Exception as e:
                return f"Error: Unable to change directory to {target_dir}. Exception: {str(e)}", 500

            # Step 4: 执行 `git pull`
            try:
                git_pull_command = "git pull"
                git_pull_process = subprocess.Popen(git_pull_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = git_pull_process.communicate()

                # 检查 `git pull` 的返回码
                if git_pull_process.returncode == 0:
                    pull_output = stdout.decode('utf-8')
                else:
                    return f"Error during git pull: {stderr.decode('utf-8')}", 500
            except Exception as e:
                return f"Error: Failed to execute 'git pull'. Exception: {str(e)}", 500

            # Step 5: 执行编译命令
            try:
                build_process = subprocess.Popen(build_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = build_process.communicate()

                # 检查命令执行的返回码
                if build_process.returncode == 0:
                    return f"Success: {stdout.decode('utf-8')}", 200
                else:
                    return f"Error during build: {stderr.decode('utf-8')}", 500
            except Exception as e:
                return f"Error: Failed to execute '{build_command}'. Exception: {str(e)}", 500

        except Exception as e:
            return f"General Exception: {str(e)}", 500