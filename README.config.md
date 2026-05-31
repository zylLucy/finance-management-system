#重要：本地配置文件说明

1. 为什么要这样做
config.py 包含数据库密码等敏感信息，绝对不能上传到 GitHub
每个人本地数据库账号 / 密码不同，各自维护自己的 config.py
仓库已配置 .gitignore，git 会自动忽略 config.py，不会误传

2. 操作步骤
#拉取最新代码
git pull origin main

#进入 backend 目录
cd backend

#复制模板为本地配置文件
复制 config.example.py，重命名为 config.py
Windows：直接复制粘贴改名
Mac/Linux：
cp config.example.py config.py

#填写自己的信息
打开 config.py，修改为你自己的数据库账号、密码、密钥：
DB_USER = "你的用户名"
DB_PASS = "你的密码"
SECRET_KEY = "自己随机生成一串"

5. 注意事项
禁止提交 config.py 到仓库
只提交 config.example.py
本地运行时，main.py 会自动 import config
