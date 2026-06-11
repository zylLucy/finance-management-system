# finance-management-system
日常记账理财管理系统



```
📁 目录结构

finance-management-system/
├── frontend/                       # 前端工程目录 (Vue 3 + Vite + Element Plus)
│   ├── index.html                  # 入口 HTML
│   ├── package.json                # 依赖配置
│   ├── vite.config.js              # Vite 构建配置
│   └── src/
│       ├── main.js                 # 应用入口
│       ├── App.vue                 # 根组件
│       ├── components/
│       │   └── charts/
│       │       ├── ExpensePieChart.vue   # 支出分类饼图
│       │       └── TrendLineChart.vue    # 收支趋势折线图
│       ├── layouts/
│       │   └── MainLayout.vue      # 主布局（侧边栏导航）
│       ├── router/
│       │   └── index.js            # 路由配置
│       ├── services/
│       │   ├── api.js              # API 接口封装
│       │   └── http.js             # Axios 实例
│       ├── stores/
│       │   ├── session.js          # 用户会话状态 (Pinia)
│       │   └── budget.js           # 预算状态 (Pinia)
│       ├── styles/
│       │   └── global.css          # 全局样式
│       ├── utils/
│       │   ├── date.js             # 日期工具函数
│       │   ├── money.js            # 金额格式化工具
│       │   └── records.js          # 账单数据处理工具
│       └── views/
│           ├── LoginView.vue       # 登录页
│           ├── RegisterView.vue    # 注册页
│           ├── DashboardView.vue   # 首页仪表盘
│           ├── RecordsView.vue     # 账单管理页
│           ├── BudgetView.vue      # 预算管理页
│           └── AiReportView.vue    # AI 财务报告页
├── backend/                        # 后端工程目录 (Python + FastAPI)
│   ├── main.py                     # 后端服务入口（路由、模型、API）
│   ├── prompt.py                   # 大模型 Prompt 模板（月度/年度）
│   ├── config.example.py           # 数据库配置模板
│   ├── .env.example                # 大模型 API 配置模板
│   └── test_db_session_lifecycle.py # 数据库会话生命周期测试
├── database/                       # 数据库设计与脚本目录
│   ├── initial_schema.sql          # 数据库建表与初始化脚本 (DDL)
│   ├── mock_data.sql               # 模拟账单数据 (DML, 5用户×12月)
│   ├── generate_mock_data.py       # 模拟数据生成脚本（多用户画像）
│   └── er_diagram.png              # 概念设计 E-R 图 / 物理模型图
├── docs/                           # 项目文档
│   ├── 需求与功能说明书.md          # 需求分析与功能说明
│   └── 错误记录.md                  # 开发过程错误记录与修复日志
├── .gitignore                      # Git 忽略文件配置
└── README.md                       # 项目说明
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
