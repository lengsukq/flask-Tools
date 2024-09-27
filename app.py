from flask import Flask, request
import os
import subprocess

app = Flask(__name__)


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    try:
        # Step 1: 检查当前工作目录
        current_dir = os.getcwd()

        # Step 2: 检查目标目录是否存在
        target_dir = '/home/code/vitePress-Web'
        if not os.path.exists(target_dir):
            return f"Error: Target directory {target_dir} does not exist", 500
        if not os.access(target_dir, os.R_OK | os.W_OK | os.X_OK):
            return f"Error: No sufficient permissions for {target_dir}", 500

        # Step 3: 改变当前工作目录
        try:
            os.chdir(target_dir)
        except Exception as e:
            return f"Error: Unable to change directory to {target_dir}. Exception: {str(e)}", 500

        # Step 4: 执行 `yarn docs:build`
        command = "yarn docs:build"
        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            # 检查命令执行的返回码
            if process.returncode == 0:
                return f"Success: {stdout.decode('utf-8')}", 200
            else:
                return f"Error during build: {stderr.decode('utf-8')}", 500
        except Exception as e:
            return f"Error: Failed to execute 'yarn docs:build'. Exception: {str(e)}", 500

    except Exception as e:
        return f"General Exception: {str(e)}", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
