# finance-management-system
日常记账理财管理系统



```
📁 目录结构

finance-management-system/
├── frontend/                  # 前端工程目录 (Vue 3 + Vite + Element Plus)
│   ├── .gitkeep               # 占位文件
│   └── src/                   # 前端源码
├── backend/                   # 后端工程目录 (Python + FastAPI)
│   ├── .gitkeep               # 占位文件
│   ├── app/                   # 后端核心业务逻辑
│   └── main.py                # 后端服务入口
├── database/                  # 数据库设计与脚本目录
│   ├── .gitkeep               # 占位文件
│   ├── initial_schema.sql     # 数据库建表与初始化脚本 (DDL)
│   ├── mock_data.sql          # 演示用财务流水伪造数据 (DML)
│   └── er_diagram.png         # 概念设计 E-R 图 / 物理模型图
├── docs/                      # 课程文档与评审物料
│   ├── .gitkeep               # 占位文件
│   ├── 需求分析与数据字典.md
│   ├── 数据库设计说明书.md
│   ├── 测试用例与评审报告.xlsx
│   └── 最终答辩展示.pptx
└── .gitignore                 # Git 忽略文件配置
```

## 👥 团队分工

- **成员 A (前端开发)**：负责 `frontend/` 目录。基于 Vue 3 和 Element Plus 搭建系统交互界面，利用 ECharts 实现账单统计图表。
- **成员 B (后端开发)**：负责 `backend/` 目录。基于 FastAPI 编写 RESTful API 接口，负责用户验证及账单 CRUD 逻辑。
- **成员 C (数据库设计)**：负责 `database/` 目录。负责 E-R 图绘制、关系模式规范化（满足3NF）、编写 SQL 脚本及触发器。
- **成员 D (测试与AI接入)**：负责 `docs/` 的测试用例撰写与全链路测试，以及在 `backend/` 中编写大模型 Prompt 调用与财务报告生成逻辑。

## ⚠️ 提交规范 (Git Commit Notice)

1. 严禁将前端的 `node_modules/` 和后端的虚拟环境 `venv/` 文件夹提交至仓库（已在 `.gitignore` 中配置）。
2. 各小组成员在各自对应的子目录下进行开发，代码提交前请先执行 `git pull` 确保代码同步，避免产生冲突。
3. 严禁在代码中硬编码暴露大模型的真实 **API Key**，请统一使用环境配置文件（如 `.env`）进行读取。
