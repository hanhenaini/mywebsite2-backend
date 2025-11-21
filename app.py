# -*- coding: utf-8 -*-
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# ==================== Flask 应用 ====================
app = Flask(__name__)
# 优化 CORS：全路径允许所有来源（测试用，生产改具体域名）
CORS(app, resources={r"/*": {"origins": "*"}})  # 改成 r"/*" 覆盖所有路由，包括 OPTIONS preflight

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


# 初始化数据库
def init_db():
    with app.app_context():
        db.create_all()
        if Project.query.count() == 0:
            projects = [
                Project(title='示例项目1', description='Flask API 开发', link='https://github.com/hanenaini/project1'),
                Project(title='示例项目2', description='前端网站构建', link='https://github.com/hanenaini/project2')
            ]
            db.session.bulk_save_objects(projects)
            db.session.commit()
            print("数据库初始化完成")


init_db()


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


@app.route('/api/projects')
def get_projects():
    projects = Project.query.all()
    data = [{'title': p.title, 'description': p.description, 'link': p.link or '#'} for p in projects]
    print(f"项目查询: 返回 {len(data)} 个项目")
    return jsonify(data)


@app.route('/api/contact', methods=['POST', 'OPTIONS'])  # 明确添加 OPTIONS 支持 preflight
def contact():
    if request.method == 'OPTIONS':
        return '', 200  # 预检请求直接返回 200

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

        # 发送邮件
        password = os.getenv('EMAIL_PASSWORD')
        if not password:
            print("警告: EMAIL_PASSWORD 未设置")
            return jsonify({"error": "服务器配置问题"}), 500

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('han02902341100@gmail.com', password)
        server.sendmail(email, 'han02902341100@gmail.com', msg.as_string())
        server.quit()

        print(f"邮件发送成功: 来自 {email}")
        return jsonify({"success": "发送成功！寒会尽快回复"}), 200
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return jsonify({"error": "发送失败，请稍后重试"}), 500


# ==================== 启动服务器 ====================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))