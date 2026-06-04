from fastapi import FastAPI, Body, Path, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, BigInteger, String, Integer, Numeric, Date, DateTime, Text, func
from sqlalchemy.ext.declarative import declarative_base
from config import DB_HOST,DB_PORT,DB_USER,DB_PASS,DB_NAME
from sqlalchemy.orm import sessionmaker
from datetime import datetime

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
    user = db.query(User).filter(User.username == username, User.password == password).first()
    if user:
        return {"code": 200, "msg": "登录成功", "data": {"user_id": user.user_id, "username": user.username}}
    return {"code": 500, "msg": "账号或密码错误"}

@app.post("/user/register")
def register(username: str = Body(...), password: str = Body(...), db = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        return {"code": 500, "msg": "用户名已存在"}
    u = User(username=username, password=password)
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
def ai_report(user_id: int, year_month: int):
    return {"code": 200, "data": "本月消费合理，继续保持！"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
