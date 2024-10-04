# routes/loveletter.py

from flask import jsonify
import psycopg2
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库连接配置
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

# 表名
TABLE_NAME = os.getenv('TABLE_NAME')

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def loveletter_route(app):
    @app.route('/loveletter', methods=['GET'])
    def get_loveletter_data():
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM {TABLE_NAME}")  # 使用环境变量中的表名
            rows = cur.fetchall()
            cur.close()
            conn.close()

            # 将查询结果转换为字典列表
            columns = [desc[0] for desc in cur.description]
            data = [dict(zip(columns, row)) for row in rows]

            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500