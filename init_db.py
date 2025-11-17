from app import app, db, Project

with app.app_context():
    db.create_all()  # 创建表
    # 清空旧数据（可选）
    Project.query.delete()

    # 添加新项目
    proj1 = Project(title="个人博客系统", description="Flask + SQLite，支持 Markdown 写作",
                    link="https://github.com/hanhenaini/blog")
    proj2 = Project(title="天气查询 App", description="React + OpenWeather API，前后端分离",
                    link="https://github.com/hanhenaini/weather")
    proj3 = Project(title="这个网站！", description="你正在看的，就是我手写的主页",
                    link="https://github.com/hanhenaini/my-website2")

    db.session.add_all([proj1, proj2, proj3])
    db.session.commit()
    print("数据库初始化成功！3 个项目已添加。")