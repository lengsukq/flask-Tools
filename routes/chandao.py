from utils.request import make_response
from flask import request
import logging
from datetime import  timedelta
logger = logging.getLogger(__name__)
import pymysql
# MySQL 数据库连接配置
db_config = {
    'host': '192.168.5.150',
    'port': 8035,
    'user': 'root',
    'password': '52b1cea071fc49789238677161b18c6c',
    'database': 'zentao',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor  # 返回字典格式的结果
}

# {
#     "activateBugNum": 0,
#     "activatedDate": null,
#     "assignedDate": "Thu, 11 May 2017 11:40:21 GMT",
#     "assignedTo": "closed",
#     "canceledBy": "",
#     "canceledDate": "Mon, 01 Jan 1979 00:00:00 GMT",
#     "closedBy": "huangh",
#     "closedDate": "Thu, 11 May 2017 11:40:21 GMT",
#     "closedReason": "done",
#     "color": "",
#     "consumed": 8,
#     "deadline": "Fri, 05 May 2017 00:00:00 GMT",
#     "delayDays": 0,
#     "deleted": "0",
#     "desc": "XNL协议设计",
#     "design": 0,
#     "designVersion": 0,
#     "entry": "",
#     "estStarted": "Mon, 24 Apr 2017 00:00:00 GMT",
#     "estimate": 8,
#     "execution": 1,
#     "feedback": 0,
#     "finishedBy": "huangh",
#     "finishedDate": "Wed, 03 May 2017 21:27:48 GMT",
#     "finishedList": "",
#     "fromBug": 0,
#     "fromIssue": 0,
#     "id": 1,
#     "keywords": "",
#     "lastEditedBy": "huangh",
#     "lastEditedDate": "Thu, 11 May 2017 11:40:21 GMT",
#     "left": 0,
#     "lines": "",
#     "mailto": "",
#     "mode": "",
#     "module": 0,
#     "mr": 0,
#     "name": "XNL协议设计",
#     "openedBy": "huangh",
#     "openedDate": "Tue, 02 May 2017 11:59:31 GMT",
#     "order": 0,
#     "overBugNum": 0,
#     "owner": "",
#     "parent": 0,
#     "planDuration": 0,
#     "pri": 2,
#     "project": 172,
#     "promisedBug": 0,
#     "realBugNum": 0,
#     "realDuration": 0,
#     "realStarted": "Tue, 02 May 2017 00:00:00 GMT",
#     "repo": 0,
#     "status": "closed",
#     "story": 0,
#     "storyVersion": 1,
#     "subStatus": "",
#     "type": "design",
#     "v1": "",
#     "v2": "",
#     "version": 0,
#     "vision": "rnd"
# },
def chandao_route(app):
    @app.route('/query_employee_scores', methods=['GET'])
    def query_employee_scores():
        try:
            # 连接数据库
            connection = pymysql.connect(**db_config)
            with connection.cursor() as cursor:
                # 执行 SQL 查询
                sql = "SELECT * FROM zt_eval_employee_score"
                cursor.execute(sql)
                result = cursor.fetchall()  # 获取所有数据

            # 关闭数据库连接
            connection.close()
            # 定义表头
            columns = [
                {"title": "账号", "dataIndex": "account", "key": "account"},
                {"title": "评论", "dataIndex": "comments", "key": "comments"},
                {"title": "ID", "dataIndex": "id", "key": "id"},
                {"title": "最后编辑人", "dataIndex": "lastEditedBy", "key": "lastEditedBy"},
                {"title": "最后编辑日期", "dataIndex": "lastEditedDate", "key": "lastEditedDate"},
                {"title": "等级", "dataIndex": "level", "key": "level"},
                {"title": "标准工作小时数", "dataIndex": "nominalWorkHours", "key": "nominalWorkHours"},
                {"title": "单次工单拒绝数", "dataIndex": "oneTicketDeny", "key": "oneTicketDeny"},
                {"title": "开启日期", "dataIndex": "openedDate", "key": "openedDate"},
                {"title": "周期", "dataIndex": "period", "key": "period"},
                {"title": "比率", "dataIndex": "ratio", "key": "ratio"},
                {"title": "总追加次数", "dataIndex": "totalAddCount", "key": "totalAddCount"},
                {"title": "总追加分数", "dataIndex": "totalAddScore", "key": "totalAddScore"},
                {"title": "总缺陷分数", "dataIndex": "totalBugScore", "key": "totalBugScore"},
                {"title": "总扣减次数", "dataIndex": "totalDeduceCount", "key": "totalDeduceCount"},
                {"title": "总扣减分数", "dataIndex": "totalDeduceScore", "key": "totalDeduceScore"},
                {"title": "总延迟天数", "dataIndex": "totalDelayDays", "key": "totalDelayDays"},
                {"title": "总延迟分数", "dataIndex": "totalDelayScore", "key": "totalDelayScore"},
                {"title": "总执行次数", "dataIndex": "totalExecutions", "key": "totalExecutions"},
                {"title": "总完成小时数", "dataIndex": "totalFinishHours", "key": "totalFinishHours"},
                {"title": "总完成度分数", "dataIndex": "totalFinishmentScore", "key": "totalFinishmentScore"},
                {"title": "总超限缺陷数", "dataIndex": "totalOverBugNum", "key": "totalOverBugNum"},
                {"title": "总计划小时数", "dataIndex": "totalPlanHours", "key": "totalPlanHours"},
                {"title": "总质量分数", "dataIndex": "totalQualityScore", "key": "totalQualityScore"},
                {"title": "总分数", "dataIndex": "totalScore", "key": "totalScore"},
                {"title": "总任务数", "dataIndex": "totalTasks", "key": "totalTasks"},
                {"title": "总工作小时分数", "dataIndex": "totalWorkHourScore", "key": "totalWorkHourScore"},
                {"title": "休假天数", "dataIndex": "vacationDays", "key": "vacationDays"}
            ]
            # 返回查询结果
            return make_response('查询成功',200,{
                "columns": columns,
                "dataSource": result
            })

        except Exception as e:
            logger.info(e)
            # 处理异常
            return make_response('查询失败',500)

    from datetime import datetime

    from datetime import datetime

    @app.route('/query_tasks', methods=['GET'])
    def query_tasks():
        try:
            # 获取查询参数
            finished_by = request.args.get('finishedBy')  # 完成人
            start_finished_date = request.args.get('start_finishedDate')  # 完成日期开始时间
            end_finished_date = request.args.get('end_finishedDate')  # 完成日期结束时间
            page = int(request.args.get('page', 1))  # 当前页码，默认为 1
            page_size = int(request.args.get('pageSize', 20))  # 每页条数，默认为 20

            # 如果没有传入日期范围，默认查询最近一个月
            if not start_finished_date or not end_finished_date:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)  # 最近一个月
                start_finished_date = start_date.strftime('%Y-%m-%d')
                end_finished_date = end_date.strftime('%Y-%m-%d')

            # 连接数据库
            connection = pymysql.connect(**db_config)
            with connection.cursor() as cursor:
                # 构建 SQL 查询（查询总数）
                count_sql = """
                    SELECT COUNT(*) AS total 
                    FROM zt_task t
                    WHERE 1=1
                """
                params = []

                # 添加完成人模糊查询条件
                if finished_by:
                    count_sql += " AND t.finishedBy LIKE %s"
                    params.append(f'%{finished_by}%')  # 添加通配符

                # 添加完成日期范围筛选条件
                if start_finished_date and end_finished_date:
                    count_sql += " AND t.finishedDate BETWEEN %s AND %s"
                    params.extend([start_finished_date, end_finished_date])

                # 执行总数查询
                cursor.execute(count_sql, params)
                total = cursor.fetchone()['total']  # 获取总条数

                # 构建 SQL 查询（查询分页数据）
                data_sql = """
                    SELECT 
                        t.name AS taskName, 
                        t.finishedBy AS finishedBy, 
                        t.finishedDate AS finishedDate,
                        t.desc AS taskDesc,
                        s.title AS storyTitle  -- 查询故事标题
                    FROM zt_task t
                    LEFT JOIN zt_story s ON t.story = s.id  -- 关联查询
                    WHERE 1=1
                """
                # 添加筛选条件
                if finished_by:
                    data_sql += " AND t.finishedBy LIKE %s"
                if start_finished_date and end_finished_date:
                    data_sql += " AND t.finishedDate BETWEEN %s AND %s"

                # 添加分页条件
                data_sql += " LIMIT %s OFFSET %s"
                offset = (page - 1) * page_size
                params.extend([page_size, offset])

                # 执行分页查询
                cursor.execute(data_sql, params)
                result = cursor.fetchall()  # 获取分页数据

            # 关闭数据库连接
            connection.close()

            # 格式化日期字段为 yyyy-mm-dd HH:MM:SS
            for task in result:
                if task['finishedDate'] and isinstance(task['finishedDate'], datetime):
                    task['finishedDate'] = task['finishedDate'].strftime('%Y-%m-%d %H:%M:%S')

            # 返回查询结果（包含分页信息）
            return make_response('查询成功', 200, {
                'data': result,
                'total': total,
                'page': page,
                'pageSize': page_size
            })

        except Exception as e:
            logger.error(f"查询失败: {e}")
            # 处理异常
            return make_response('查询失败', 500)