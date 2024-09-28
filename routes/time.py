from flask import jsonify
from datetime import datetime
import pytz

def get_current_time(timezone):
    tz = pytz.timezone(timezone)
    return datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

def time_route(app):
    @app.route('/time', methods=['GET'])
    def get_beijing_time():
        beijing_time = get_current_time('Asia/Shanghai')
        return jsonify({'beijing_time': beijing_time})

    @app.route('/USAtime', methods=['GET'])
    def get_usa_time():
        usa_time = get_current_time('America/New_York')
        return jsonify({'usa_time': usa_time})

    @app.route('/hktime', methods=['GET'])
    def get_hong_kong_time():
        hong_kong_time = get_current_time('Asia/Hong_Kong')
        return jsonify({'hong_kong_time': hong_kong_time})

    # 日本
    @app.route('/jptime', methods=['GET'])
    def get_japanese_time():
        japanese_time = get_current_time('Asia/Tokyo')
        return jsonify({'japanese_time': japanese_time})