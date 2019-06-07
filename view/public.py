# coding:utf-8
import functools

from flask import Blueprint, make_response, render_template, current_app, request
from tools import timestamp,string_time
from model.article.article import Article

view_of_public = Blueprint("view_of_public", __name__)

def view_cache(func):
    '''缓存视图函数
    参数：
        func Function 视图函数
    输出：
        response
        
    '''
    @functools.wraps(func)
    def dec(*args,**kwargs):
        # 基于路由,查询缓存
        path = request.path
        c = current_app.config["kv_cache"].get(key=path)
        if c["code"] == 200:
            return c["value"],200,{"x-cache-status":"hit","x-cache-at":c["timestamp"]}
            
        # 未命中缓存时新建缓存
        else:
            view = func(*args,**kwargs)
            c = current_app.config["kv_cache"].put(key=path,value=view)
            if c["code"] == 200:
                c = current_app.config["kv_cache"].get(key=path)
                if c["code"] == 200:
                    # 重建成功
                    return c["value"],{"x-cache-status":"miss 0"}
                else:
                    # 读取缓存失败
                    return view,200,{"x-cache-status":"miss 1"}
            else:
                # 写入缓存失败
                return view,200,{"x-cache-status":"miss 2"}
    return dec


@view_of_public.route("/", methods=["GET"])
@view_cache
def index_by_get():
    '''文章流'''
    query = Article().all()
    if query["code"] == 200:
        feeds = []
        for r in query["records"]:
            feeds.append({'id':r.id,'title':r.title,'brief':r.brief})
        return render_template("article-feed.html",feeds=feeds)
    else:
        return render_template("article-feed.html",feeds=None)


@view_of_public.route("/article/<id>", methods=["GET"])
@view_cache
def query_article_by_id(id):
    '''文章详情'''
    query = Article().one(id=id)
    if query["code"] == 200:
        article = query["record"]
        return render_template("article.html",article={'title':article.title,'brief':article.brief,'content':article.content,'string_time':string_time(ts = article.timestamp)})
    else:
        return render_template("notice.html", message={'code':'404','type':'错误','body':'该文章不可用'})

