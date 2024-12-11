import requests
from flask import jsonify
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def gitlab_route(app):
    @app.route('/gitlab', methods=['GET'])
    def gitlab():
        # 定义请求头，包含 Cookie
        headers = {
            "Cookie": "sidebar_collapsed=false; remember_user_token=W1s4Nl0sIiQyYSQxMCRyQW05ZXouanUxVFJiLkZmcGhxZVVlIiwiMTczMzgxOTM3NC4xOTU5OTQ0Il0%3D--71366919a43f0aa993301e4a2a6c5cf6e7032ce1; _gitlab_session=f3a7e083e6963075a9822fc580887eef"  # 替换为实际的 Cookie 值
        }

        # 存储所有用户的结果
        results = []
        usernames = ['tanghongxin', 'wangxue', 'yewenjie', 'liuzeqiong', 'huangmingyu', 'jiangyimin', 'jiangluya']

        # 遍历用户名列表
        for username in usernames:
            # 构建请求URL
            url = f"http://192.168.4.198:6518/users/{username}/calendar.json"

            # 发送GET请求，带上 Cookie
            response = requests.get(url, headers=headers)

            # 检查请求是否成功
            if response.status_code == 200:
                # 解析返回的数据
                commit_data = response.json()

                # 检查是否有数据
                if not commit_data:
                    results.append({
                        "username": username,
                        "start_date": None,
                        "end_date": None,
                        "total_commits": 0,
                        "commit_days": 0,
                        "average_commits_per_day": 0
                    })
                    continue

                # 提取所有日期
                dates = list(commit_data.keys())

                # 获取开始日期和结束日期
                start_date = min(dates)  # 最早的日期
                end_date = max(dates)  # 最晚的日期

                # 计算所有日期的提交次数总和
                total_commits = sum(commit_data.values())

                # 统计提交的天数
                commit_days = len([commits for commits in commit_data.values() if commits > 0])

                # 计算日均提交次数
                if commit_days > 0:
                    average_commits_per_day = total_commits / commit_days
                else:
                    average_commits_per_day = 0

                # 使用 logger 打印结果
                logger.info("User: %s, Start date: %s, End date: %s, Total commits: %d, Commit days: %d, Average commits per day: %.2f",
                            username, start_date, end_date, total_commits, commit_days, average_commits_per_day)

                # 添加结果到列表
                results.append({
                    "username": username,
                    "start_date": start_date,
                    "end_date": end_date,
                    "total_commits": total_commits,
                    "commit_days": commit_days,
                    "average_commits_per_day": round(average_commits_per_day, 2)
                })
            else:
                # 如果请求失败，记录错误信息
                logger.error("Failed to fetch commit data for user %s. Status code: %s",
                             username, response.status_code)

                # 添加错误结果到列表
                results.append({
                    "username": username,
                    "error": f"Failed to fetch commit data. Status code: {response.status_code}"
                })

        # 按照提交次数从高到低排序
        results_sorted = sorted(results, key=lambda x: x.get('total_commits', 0), reverse=True)

        # 返回排序后的结果
        return jsonify(results_sorted)