# -*- coding: utf-8 -*-
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# ==================== Flask 应用 ====================
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # 允许所有来源访问 /api/*

# ==================== 数据库配置 ====================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'projects.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ==================== 项目模型 ====================
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    link = db.Column(db.String(200))

# 创建表
with app.app_context():
    db.create_all()

# ==================== 路由 ====================

@app.route('/')
def home():
    return '''
    <div style="text-align:center; margin-top:100px; font-family:Arial;">
        <h1>后端运行中！</h1>
        <p>访问 <a href="/api/projects">/api/projects</a> 查看项目</p>
    </div>
    '''

@app.route('/api/hello')
def hello():
    return jsonify({"message": "你好，寒的后端！", "status": "running"})

# --- 获取项目 ---
@app.route('/api/projects')
def get_projects():
    projects = Project.query.all()
    data = [{
        'title': p.title,
        'description': p.description,
        'link': p.link or '#'
    } for p in projects]
    return jsonify(data)  # 自动处理 CORS + 中文

# --- 联系表单发送邮件 ---
@app.route('/api/contact', methods=['POST'])
def contact():
    try:
        data = request.get_json()
        name = data.get('name', '匿名')
        email = data.get('email')
        message = data.get('message')

        if not email or '@' not in email or not message:
            return jsonify({"error": "请填写有效邮箱和消息"}), 400

        # 构造邮件
        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = 'han02902341100@gmail.com'
        msg['Subject'] = f"网站来信：{name}"
        body = f"姓名: {name}\n邮箱: {email}\n\n消息:\n{message}"
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # 发送邮件（使用环境变量密码）
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('han02902341100@gmail.com', os.getenv('EMAIL_PASSWORD'))  # 使用环境变量
        server.sendmail(email, 'han02902341100@gmail.com', msg.as_string())
        server.quit()

        return jsonify({"success": "发送成功！寒会尽快回复"}), 200

    except Exception as e:
        print("邮件发送失败:", e)
        return jsonify({"error": "发送失败，请稍后重试"}), 500

# ==================== 启动服务器 ====================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))  # 生产环境端口支持