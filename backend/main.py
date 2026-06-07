from fastapi import FastAPI, Body, Path, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, BigInteger, String, Integer, Numeric, Date, DateTime, Text, func
from sqlalchemy.ext.declarative import declarative_base
from config import DB_HOST,DB_PORT,DB_USER,DB_PASS,DB_NAME
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from collections import defaultdict
import bcrypt
import os
from dotenv import load_dotenv
from openai import OpenAI
from prompt import build_financial_prompt, build_yearly_prompt

# 加载 .env 环境变量
load_dotenv()

# 大模型客户端配置
llm_client = OpenAI(
    api_key=os.getenv("LLM_API_KEY", ""),
    base_url=os.getenv("LLM_BASE_URL") or None
)
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# ====================
# 日常记账理财管理系统
# ====================

app = FastAPI(title="日常记账理财管理系统", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================== 数据库连接 ======================
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ====================== 官方数据库表结构 ======================
class User(Base):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    register_time = Column(DateTime, default=datetime.now)

class Category(Base):
    __tablename__ = "category"
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(50), nullable=False)
    type = Column(String(20), nullable=False)  # income / expense

class MonthlyBudget(Base):
    __tablename__ = "monthly_budget"
    user_id = Column(Integer, primary_key=True)
    year_month = Column(Integer, primary_key=True)
    amount = Column(Numeric(10,2), nullable=False)

class BillRecord(Base):
    __tablename__ = "bill_record"
    record_id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Numeric(10,2), nullable=False)
    date = Column(Date, nullable=False)
    remark = Column(String(255), nullable=True)
    user_id = Column(Integer, nullable=False)
    category_id = Column(Integer, nullable=False)

class AIReport(Base):
    __tablename__ = "ai_report"
    report_id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    year_month = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ====================== 接口 ======================

@app.post("/user/login")
def login(username: str = Body(...), password: str = Body(...), db = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return {"code": 500, "msg": "账号或密码错误"}
    if not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        return {"code": 500, "msg": "账号或密码错误"}
    return {"code": 200, "msg": "登录成功", "data": {"user_id": user.user_id, "username": user.username}}

@app.post("/user/register")
def register(username: str = Body(...), password: str = Body(...), db = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        return {"code": 500, "msg": "用户名已存在"}
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    u = User(username=username, password=hashed)
    db.add(u)
    db.commit()
    return {"code": 200, "msg": "注册成功"}

@app.get("/category/list/{user_id}")
def list_category(user_id: int = Path(...), db = Depends(get_db)):
    ls = db.query(Category).all()
    res = [{"id": i.category_id, "name": i.category_name, "type": i.type} for i in ls]
    return {"code": 200, "data": res}

@app.post("/record/add")
def add_record(
    user_id: int = Body(...),
    category_id: int = Body(...),
    amount: float = Body(...),
    date: str = Body(...),
    remark: str = Body(None),
    db = Depends(get_db)
):
    r = BillRecord(
        user_id=user_id,
        category_id=category_id,
        amount=amount,
        date=date,
        remark=remark
    )
    db.add(r)
    db.commit()
    return {"code": 200, "msg": "记账成功"}

@app.get("/record/list/{user_id}")
def get_records(user_id: int = Path(...), db = Depends(get_db)):
    records = db.query(BillRecord).filter(BillRecord.user_id == user_id).all()
    res = [
        {
            "id": r.record_id,
            "amount": float(r.amount),
            "date": str(r.date),
            "remark": r.remark,
            "category_id": r.category_id
        } for r in records
    ]
    return {"code": 200, "data": res}

@app.post("/budget/save")
def save_budget(user_id: int = Body(...), year_month: int = Body(...), amount: float = Body(...), db = Depends(get_db)):
    b = db.query(MonthlyBudget).filter(MonthlyBudget.user_id == user_id, MonthlyBudget.year_month == year_month).first()
    if b:
        b.amount = amount
    else:
        b = MonthlyBudget(user_id=user_id, year_month=year_month, amount=amount)
        db.add(b)
    db.commit()
    return {"code": 200, "msg": "预算保存成功"}

@app.get("/record/today/{user_id}")
def today_stats(user_id: int = Path(...), db = Depends(get_db)):
    today = datetime.now().strftime("%Y-%m-%d")
    income = db.query(func.coalesce(func.sum(BillRecord.amount), 0)).filter(
        BillRecord.user_id == user_id,
        BillRecord.date == today,
        BillRecord.category_id.in_([6,7,8,9])
    ).scalar()
    expense = db.query(func.coalesce(func.sum(BillRecord.amount), 0)).filter(
        BillRecord.user_id == user_id,
        BillRecord.date == today,
        BillRecord.category_id.in_([1,2,3,4,5])
    ).scalar()
    return {"code": 200, "data": {"income": float(income), "expense": float(expense)}}

@app.get("/report/ai/{user_id}/{year_month}")
def ai_report(user_id: int, year_month: int, db = Depends(get_db)):
    """
    获取或生成 AI 财务报告。
    先查数据库缓存，若不存在则聚合当月数据调大模型生成，存入数据库后返回。
    """

    # 1. 查询缓存
    existing = db.query(AIReport).filter(
        AIReport.user_id == user_id,
        AIReport.year_month == year_month
    ).first()
    if existing:
        return {"code": 200, "data": existing.content, "cached": True}

    # 2. 聚合当月账单数据
    records = db.query(BillRecord).filter(
        BillRecord.user_id == user_id,
        func.date_format(BillRecord.date, "%Y%m") == str(year_month)
    ).all()

    if not records:
        return {"code": 500, "msg": f"该月份暂无账单记录，无法生成报告"}

    # 获取分类映射
    categories = {c.category_id: c for c in db.query(Category).all()}

    # 3. 计算聚合数据
    total_income = 0.0
    total_expense = 0.0
    income_map = defaultdict(float)
    expense_map = defaultdict(float)
    daily_trend_map = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
    top_expenses = []

    for r in records:
        cat = categories.get(r.category_id)
        cat_name = cat.category_name if cat else "未知"
        cat_type = cat.type if cat else "expense"
        amount = float(r.amount)

        if cat_type == "income":
            total_income += amount
            income_map[cat_name] += amount
        else:
            total_expense += amount
            expense_map[cat_name] += amount
            if amount > 100:
                top_expenses.append({
                    "date": str(r.date),
                    "category": cat_name,
                    "amount": amount,
                    "remark": r.remark or ""
                })

        daily_trend_map[str(r.date)]["income" if cat_type == "income" else "expense"] += amount

    balance = total_income - total_expense

    # 预算
    budget = db.query(MonthlyBudget).filter(
        MonthlyBudget.user_id == user_id,
        MonthlyBudget.year_month == year_month
    ).first()
    budget_amount = float(budget.amount) if budget else 0.0
    budget_remaining = budget_amount - total_expense if budget_amount > 0 else 0.0

    # 收入构成
    income_breakdown = sorted(
        [{"category": k, "amount": round(v, 2), "percent": round(v / total_income * 100, 1) if total_income > 0 else 0}
         for k, v in income_map.items()],
        key=lambda x: x["amount"], reverse=True
    )

    # 支出构成
    expense_breakdown = sorted(
        [{"category": k, "amount": round(v, 2), "percent": round(v / total_expense * 100, 1) if total_expense > 0 else 0}
         for k, v in expense_map.items()],
        key=lambda x: x["amount"], reverse=True
    )

    # 每日趋势
    daily_trend = sorted(
        [{"date": d, "income": round(v["income"], 2), "expense": round(v["expense"], 2)}
         for d, v in daily_trend_map.items()],
        key=lambda x: x["date"]
    )

    # 大额消费排名
    top_expenses = sorted(top_expenses, key=lambda x: x["amount"], reverse=True)[:10]

    user_data = {
        "year_month": year_month,
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "balance": round(balance, 2),
        "budget": round(budget_amount, 2),
        "budget_remaining": round(budget_remaining, 2),
        "income_breakdown": income_breakdown,
        "expense_breakdown": expense_breakdown,
        "daily_trend": daily_trend,
        "top_expenses": top_expenses
    }

    # 4. 调用大模型
    prompt = build_financial_prompt(user_data)

    try:
        response = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "你是一位专业的理财顾问，请用中文回复。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4096
        )
        report_content = response.choices[0].message.content
    except Exception as e:
        # API 调用失败时返回聚合数据，方便调试
        return {
            "code": 500,
            "msg": f"大模型调用失败: {str(e)}",
            "debug_data": user_data
        }

    # 5. 存入数据库
    report = AIReport(user_id=user_id, year_month=year_month, content=report_content)
    db.add(report)
    db.commit()

    return {"code": 200, "data": report_content, "cached": False}


@app.get("/report/ai/{user_id}/year/{year}")
def ai_year_report(user_id: int, year: int, db = Depends(get_db)):
    """
    获取或生成年度 AI 财务报告。
    聚合全年 12 个月数据，调用大模型生成年度分析报告。
    缓存策略：year_month 使用 year * 100 作为年度报告标识。
    """

    year_month_key = year * 100  # 年度报告缓存键

    # 1. 查询缓存
    existing = db.query(AIReport).filter(
        AIReport.user_id == user_id,
        AIReport.year_month == year_month_key
    ).first()
    if existing:
        return {"code": 200, "data": existing.content, "cached": True}

    # 2. 聚合全年数据
    records = db.query(BillRecord).filter(
        BillRecord.user_id == user_id,
        func.date_format(BillRecord.date, "%Y") == str(year)
    ).all()

    if not records:
        return {"code": 500, "msg": f"{year}年暂无账单记录，无法生成年度报告"}

    categories = {c.category_id: c for c in db.query(Category).all()}

    # 3. 按月份聚合
    monthly_data = defaultdict(lambda: {
        "income": 0.0, "expense": 0.0,
        "by_cat": defaultdict(float)
    })
    year_total_income = 0.0
    year_total_expense = 0.0
    year_cat_totals = defaultdict(float)
    top_expenses = []

    for r in records:
        cat = categories.get(r.category_id)
        cat_name = cat.category_name if cat else "未知"
        cat_type = cat.type if cat else "expense"
        amount = float(r.amount)
        month_key = r.date.strftime("%Y-%m")

        if cat_type == "income":
            monthly_data[month_key]["income"] += amount
            year_total_income += amount
        else:
            monthly_data[month_key]["expense"] += amount
            monthly_data[month_key]["by_cat"][cat_name] += amount
            year_total_expense += amount
            year_cat_totals[cat_name] += amount
            if amount > 200:
                top_expenses.append({
                    "date": str(r.date),
                    "category": cat_name,
                    "amount": amount,
                    "remark": r.remark or ""
                })

    # 月度摘要
    monthly_summary = []
    balance_trend = []
    peak_month = {"month": "", "expense": 0}
    for month_key in sorted(monthly_data.keys()):
        d = monthly_data[month_key]
        balance = d["income"] - d["expense"]
        # 查预算
        ym = int(month_key.replace("-", ""))
        budget_row = db.query(MonthlyBudget).filter(
            MonthlyBudget.user_id == user_id,
            MonthlyBudget.year_month == ym
        ).first()
        budget = float(budget_row.amount) if budget_row else 0.0
        budget_usage = (d["expense"] / budget * 100) if budget > 0 else 0.0
        top_cat = max(d["by_cat"].items(), key=lambda x: x[1]) if d["by_cat"] else ("无", 0)

        monthly_summary.append({
            "month": month_key,
            "income": round(d["income"], 2),
            "expense": round(d["expense"], 2),
            "balance": round(balance, 2),
            "budget": round(budget, 2),
            "budget_usage": round(budget_usage, 1),
            "top_expense_cat": top_cat[0],
            "top_expense_amount": round(top_cat[1], 2)
        })
        balance_trend.append(round(balance, 2))
        if d["expense"] > peak_month["expense"]:
            peak_month = {"month": month_key, "expense": d["expense"]}

    # 分类年度汇总
    category_annual = []
    for cat_name, total in sorted(year_cat_totals.items(), key=lambda x: x[1], reverse=True):
        category_annual.append({
            "category": cat_name,
            "total": round(total, 2),
            "avg_monthly": round(total / 12, 2),
            "percent": round(total / year_total_expense * 100, 1) if year_total_expense > 0 else 0
        })

    top_expenses = sorted(top_expenses, key=lambda x: x["amount"], reverse=True)[:15]

    user_data = {
        "year": year,
        "year_total_income": round(year_total_income, 2),
        "year_total_expense": round(year_total_expense, 2),
        "year_balance": round(year_total_income - year_total_expense, 2),
        "peak_month": peak_month["month"],
        "monthly_summary": monthly_summary,
        "category_annual": category_annual,
        "top_expenses": top_expenses,
        "monthly_balance_trend": balance_trend
    }

    # 4. 调用大模型
    prompt = build_yearly_prompt(user_data)

    try:
        response = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "你是一位专业的理财顾问，请用中文回复。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4096
        )
        report_content = response.choices[0].message.content
    except Exception as e:
        return {
            "code": 500,
            "msg": f"大模型调用失败: {str(e)}",
            "debug_data": user_data
        }

    # 5. 存入数据库（year_month = year * 100）
    report = AIReport(user_id=user_id, year_month=year_month_key, content=report_content)
    db.add(report)
    db.commit()

    return {"code": 200, "data": report_content, "cached": False}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
