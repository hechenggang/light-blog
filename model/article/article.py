# coding=utf-8
import os
import functools

from flask import request, jsonify, make_response, Blueprint
from tools import timestamp

# 建立数据模型
MODULE_PATH = os.path.split(__file__)[0]
from sqlalchemy import Column, String, Integer, create_engine, func, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
DB_PATH = os.path.join(MODULE_PATH, "article.db")
ENGINE = create_engine("sqlite:///" + DB_PATH, connect_args={'check_same_thread': False})
SESSION = sessionmaker(bind=ENGINE)
Base = declarative_base()
class DB(Base):
    """
    文章数据模型
    id 自增
    title 标题
    brief 摘要
    content 正文
    timestamp 时间戳
    """
    __tablename__ = "article"

    id = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(String(50))
    brief = Column(String(500))
    content = Column(String(50000))
    timestamp = Column(Integer)
    
try:
    Base.metadata.create_all(ENGINE)
except:
    pass
#使用 SESSION 调用一個实例 session = SESSION(bind=ENGINE.connect())


class Article:
    """文章操作类"""

    def new(self,title=None,brief=None,content=None,ts=None):
        '''
        描述：新建文章
        参数：
            title String 0<len<50 文章标题
            brief String 0<len<500 文章摘要
            content String 0<len<50000 文章正文

        返回：
            {"code": 200}
            {"code": 4**, "errmsg":...}

        '''

        # 检查输入
        if not bool(title):
            return {"code": 400, "errmsg": "缺少标题"}
        elif not bool(brief):
            return {"code": 400, "errmsg": "缺少摘要"}
        elif not bool(content):
            return {"code": 400, "errmsg": "缺少正文"}
        else:
            pass

        if bool(ts):
            ts = int(ts)
        else:
            ts = timestamp()
        session = SESSION(bind=ENGINE.connect())
        a = DB(
            title = title,
            brief = brief,
            content = content,
            timestamp = ts
        )
        session.add(a)
        session.commit()
        session.close()
        return {"code": 200}


    def delete(self,id=None):
        '''
        描述：删除文章
        参数：
            id Integer 文章唯一标识
        返回：
            {"code": 200}
            {"code": 4**, "errmsg":...}

        '''
        if not bool(id):
            return {"code": 400, "errmsg": "缺少文章唯一标识"}

        session = SESSION(bind=ENGINE.connect())
        record = session.query(DB).filter(DB.id == id).first()
        if not record:
            return {"code": 404, "errmsg": "文章不存在"}
        else:
            session.delete(record)
            session.commit()
            session.close()
            return {"code": 200}


    def all(self,limit=1000,offset=0):
        '''
        描述：所有文章
        参数：
            limit Integer 需要数量
            offset Integer 需要数量

        返回：
            {"code": 200,"records":records}
            {"code": 4**, "errmsg":...}

        '''

        session = SESSION(bind=ENGINE.connect())
        records = (
            session.query(DB)
            .order_by(desc(DB.id))
            .limit(limit)
            .offset(offset)
            .all()
        )
        session.close()
        return {"code": 200,"records":records}

    def one(self,id=None):
        '''
        描述：根据 id 查询一篇文章
        参数：
            id Integer 文章唯一标识

        返回：
            {"code": 200,"record":record}
            {"code": 4**, "errmsg":...}

        '''

        session = SESSION(bind=ENGINE.connect())
        record = session.query(DB).filter(DB.id == id).first()
        session.close()
        if record:
            return {"code": 200,"record":record}
        else:
            return {"code": 404,"errmsg":"未找到该文章"}

    def update(self,id=None,title=None,brief=None,content=None):
        '''
        描述：更新文章
        参数：
            id Integer  文章唯一标识
            title String 0<len<50 文章标题
            brief String 0<len<500 文章摘要
            content String 0<len<5000 文章正文

        返回：
            {"code": 200}
            {"code": 4**, "errmsg":...}

        '''

        # 检查输入
        if not bool(title):
            return {"code": 400, "errmsg": "缺少标题"}
        elif not bool(brief):
            return {"code": 400, "errmsg": "缺少摘要"}
        elif not bool(content):
            return {"code": 400, "errmsg": "缺少正文"}
        elif not bool(id):
            return {"code": 400, "errmsg": "缺少唯一标识"}
        else:
            pass

        if not(0 < len(title) < 50):
            return {"code": 400, "errmsg": "标题长度应小于50个字符"}
        elif not(0 < len(brief) < 500):
            return {"code": 400, "errmsg": "摘要长度应小于500个字符"}
        elif not(0 < len(content) < 50000):
            return {"code": 400, "errmsg": "正文长度应小于5000个字符"}
        else:
            pass

        session = SESSION(bind=ENGINE.connect())
        a = session.query(DB).filter(DB.id == id).first()
        if a:
            a.title = title
            a.brief = brief
            a.content = content
            session.add(a)
            session.commit()
            session.close()
            return {"code": 200}

        else:
            session.close()
            return {"code": 500,"errmsg":"内部错误"}




    # # 更新用户
    # @staticmethod
    # def update(
    #     user_id=None,
    #     update_data={
    #         "password": None,
    #         "salt": None,
    #         "when_try_activate": None,
    #         "when_try_reset_password": None,
    #         "status": None
    #     }
    # ):
    #     '''
    #     描述：更新用户信息
    #     参数：
    #         @user_id(String) -- 用户 id
    #         @update_data(Dict) -- 用户信息
    #     返回：
    #         {"code": 200}
    #         {"code": 4**}

    #     '''
    #     session = SESSION(bind=ENGINE.connect())
    #     record = session.query(DB).filter(DB.id == user_id).first()
    #     if record:
    #         if "status" in update_data:
    #             record.status = update_data["status"]
    #         if "when_try_activate" in update_data:
    #             record.when_try_activate = update_data["when_try_activate"]
    #         if "when_try_reset_password" in update_data:
    #             record.when_try_reset_password = update_data["when_try_reset_password"]
    #         if "password" in update_data:
    #             record.password = update_data["password"]
    #         if "salt" in update_data:
    #             record.salt = update_data["salt"]

    #         session.commit()
    #         session.close()
    #         return {"code": 200}

    #     else:
    #         session.close()
    #         return {"code": 404}
