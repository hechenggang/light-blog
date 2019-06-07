# coding:utf-8
import functools

from flask import Blueprint, make_response, current_app, render_template, request, session, redirect, jsonify, url_for
from tools import timestamp
from model.article.article import Article

view_of_admin = Blueprint("view_of_admin", __name__)


def authorize(function):
    '''
    装饰一个视图方法，
    基于 session 进行鉴权，
    根据鉴权结果决定是否返回被装饰的视图的结果。
    '''
    @functools.wraps(function)
    def decoration(*args, **kwargs):
        if ("admin_username" in session):
            if session['admin_username'] == current_app.config["admin_username"]:
                return function(*args, **kwargs)
            else:
                return redirect('/admin/login')
        else:
            return redirect('/admin/login')
    return decoration



@view_of_admin.route("/login", methods=["GET"])
def get_login():
    return render_template("login.html")


@view_of_admin.route("/login", methods=["POST"])
def post_login():
    '''超级简单的单一用户校验'''

    if ('username' in request.form) and ('password' in request.form):
        if (request.form['username'] == current_app.config["admin_username"])and(request.form['password'] == current_app.config["admin_password"]):
            session['admin_username'] = current_app.config["admin_username"]
            return redirect('/admin/manage')
        else:
            return render_template("notice.html", message={'code':'403','type':'错误','body':'账号或密码不正确'}),403

    else:
        return render_template("notice.html", message={'code':'400','type':'错误','body':'参数错误'}),400


@view_of_admin.route("/manage", methods=["GET"])
@authorize
def get_admin():
    query = Article().all()
    if query["code"] == 200:
        feeds = []
        for r in query["records"]:
            feeds.append({'id':r.id,'title':r.title,'brief':r.brief})
        return render_template("admin.html",feeds=feeds)
    else:
        return render_template("admin.html",feeds=None)

    


@view_of_admin.route("/article", methods=["POST"])
@authorize
def post_article():
    '''保存文章'''
    
    data = {'title':None,'brief':None,'content':None}
    for key in data.keys():
        if (key not in request.form)or(len(request.form[key]) < 1):
            return jsonify({'code':'400','type':'错误','body':'{} 需要被填写'.format(key)}),400
        data[key] = request.form[key]
    
    if "id" not in request.form:
        return "",400
    else:
        id = request.form['id']
        if len(id)>0:

            # 更新文章
            r = Article().update(id=id,title=data['title'],brief=data['brief'],content=data['content'])
            if r["code"] == 200:
                # 删除缓存,主页和更新的文章页
                path = url_for("view_of_public.query_article_by_id",id=id)
                c = current_app.config["kv_cache"].delete(key=path)
                path = url_for("view_of_public.index_by_get")
                c = current_app.config["kv_cache"].delete(key=path)

                return jsonify({'code':'200','type':'成功','body':'更新成功'})
            else:
                return jsonify({'code':r["code"],'type':'错误','body':r["errmsg"]}),r["code"]
        else:

            # 新建文章
            r = Article().new(title=data['title'],brief=data['brief'],content=data['content'])
            if r["code"] == 200:
                # 删除缓存
                path = url_for("view_of_public.index_by_get")
                c = current_app.config["kv_cache"].delete(key=path)

                return jsonify({'code':'200','type':'成功','body':'提交成功'})
            else:
                return jsonify({'code':r["code"],'type':'错误','body':r["errmsg"]}),r["code"]



@view_of_admin.route("/new", methods=["GET"])
@authorize
def get_new():
    '''新建文章'''
    return render_template("editor.html",data={'name':'新建文章'})


@view_of_admin.route("/delete/<id>", methods=["GET"])
@authorize
def get_delete(id):
    '''删除文章''' 
    r = Article().delete(id=id)
    if r["code"] == 200:
        # 删除缓存
        path = url_for("view_of_public.index_by_get")
        c = current_app.config["kv_cache"].delete(key=path)
        return redirect('/admin/manage')
    else:
        return render_template("notice.html", message={'code':r["code"],'type':'错误','body':r["errmsg"]})


@view_of_admin.route("/update/<id>", methods=["GET"])
@authorize
def get_update(id):
    '''修改文章'''
    r = Article().one(id=id)
    if r["code"] == 200:
        article = r["record"]
        return render_template("editor.html",data={'name':'更新文章','id':article.id,'title':article.title,'brief':article.brief,'content':article.content})
    else:
        return "404"

@view_of_admin.route("/logout", methods=["GET"])
@authorize
def get_logout():
    '''退出'''
    session.clear()
    return redirect('/')
