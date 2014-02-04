#encoding=utf-8

from flask import Flask, g, request, render_template, flash, redirect, url_for
import MySQLdb

import sys  
reload(sys) 
sys.setdefaultencoding('utf8')   

import imp
try:
    imp.find_module("sae")
    from sae.const import (MYSQL_HOST, MYSQL_HOST_S, MYSQL_PORT, 
               MYSQL_USER, MYSQL_PASS, MYSQL_DB)
except ImportError:
    from config.local_config import (MYSQL_HOST, MYSQL_HOST_S, MYSQL_PORT, 
                         MYSQL_USER, MYSQL_PASS, MYSQL_DB)

app = Flask(__name__)
app.debug = True
app.secret_key = 'guesswhatkeyitis'


@app.before_request
def before_request():
    g.db = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS,
               MYSQL_DB, port=int(MYSQL_PORT), charset="utf8") #Define charset to avoid chinese decode error

#请求结束时关闭数据库连接
@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

##############################################
#
# provide gobal method or variable for jinja2
#
##############################################
@app.context_processor
def get_menu():
    def get_menu():
        sql = """SELECT `id`, `title` 
                 FROM `columns` 
                 WHERE `is_delete` <> 1 
                 ORDER BY `order`; """
        cursor = g.db.cursor()
        cursor.execute(sql)
        columns = [dict(id=column[0], title=column[1]) 
                        for column in cursor.fetchall()]
        return columns
    return dict(get_menu=get_menu)



##############################################
#
#
# website
#
#
##############################################

@app.route('/')
def index():
    return render_template("index.html", index="now")

@app.route('/apply/report_outter')
def report_outter():
    return render_template("report-basic.html", report_outter="now")

##############################################
#
#
# admin
#
##############################################

@app.route('/admin')
def admin_index():
    return render_template("admin/basic.html")

####################
#
# column management
#
####################
@app.route('/admin/column')
def admin_column():
    sql = """SELECT `id`, `title` 
             FROM `columns` 
             WHERE `is_delete` <> 1 
             ORDER BY `order`; """
    cursor = g.db.cursor()
    cursor.execute(sql)
    columns = [dict(id=column[0], title=column[1]) for column in cursor.fetchall()]
    return render_template("admin/column.html", column="active", columns=columns)

@app.route('/admin/column/add', methods=['POST'])
def admin_column_add():
    sql_search = """SELECT MAX(`id`) 
                    FROM `columns` 
                    WHERE `is_delete` = 0 """
    sql = """INSERT INTO `columns` (`title`, `order`) 
             VALUES ( %s, %s ); """
    if request.method == 'POST' :
        title = request.form['title']
        cursor = g.db.cursor()
        cursor.execute(sql_search)
        max_id = cursor.fetchall()[0][0]
        if max_id:
            max_id = max_id + 1
        else :
            max_id = 1
        cursor.execute(sql, (title, max_id))
        g.db.commit()
    return redirect(url_for("admin_column"))

@app.route('/admin/column/del/<int:post_id>')
def admin_column_del(post_id):
    sql = """UPDATE `columns` 
             SET `is_delete` =  '1' 
             WHERE  `columns`.`id` = %s;"""
    cursor = g.db.cursor()
    cursor.execute(sql, (post_id, ))
    g.db.commit()
    return redirect(url_for("admin_column"))

@app.route('/admin/column/<int:post_id>/up')
def admin_column_up(post_id):
    sql_search = """SELECT `id`, `order` FROM `columns` 
                    WHERE `is_delete` <> 1
                    AND `parent_id` = 0
                    ORDER BY `order`; """
    sql_update = """UPDATE `columns`
                    SET `order` = %s 
                    WHERE `id` = %s;"""
    cursor = g.db.cursor()
    cursor.execute(sql_search)
    columns = list(cursor.fetchall())
    column_pre_id = post_id
    column_pre_order = None
    column_now_order = None
    for column in columns:
        if column[0] != post_id:
            column_pre_id = column[0]
            column_pre_order = column[1]
        else :
            column_now_id = column[0]
            column_now_order = column[1]
            break
    if column_now_order and column_pre_order :
        cursor.execute(sql_update, (column_pre_order, post_id))
        cursor.execute(sql_update, (column_now_order, column_pre_id))
        g.db.commit()
    return redirect(url_for("admin_column"))


@app.route('/admin/column/<int:post_id>/down')
def admin_column_down(post_id):
    sql_search = """SELECT `id`, `order` FROM `columns` 
                    WHERE `is_delete` <> 1
                    AND `parent_id` = 0
                    ORDER BY `order` desc; """
    sql_update = """UPDATE `columns`
                    SET `order` = %s 
                    WHERE `id` = %s;"""
    cursor = g.db.cursor()
    cursor.execute(sql_search)
    columns = list(cursor.fetchall())
    column_pre_id = post_id
    column_pre_order = None
    column_now_order = None
    for column in columns:
        if column[0] != post_id:
            column_pre_id = column[0]
            column_pre_order = column[1]
        else :
            column_now_id = column[0]
            column_now_order = column[1]
            break
    if column_now_order and column_pre_order :
        cursor.execute(sql_update, (column_pre_order, post_id))
        cursor.execute(sql_update, (column_now_order, column_pre_id))
        g.db.commit()
    return redirect(url_for("admin_column"))

###############################
#
# content management
#
###############################

@app.route('/admin/content')
def admin_content():
    return render_template("admin/content-edit.html", content="active")

@app.route('/admin/form')
def admin_index():
    return render_template("admin/basic.html", form="active")

if "__main__" == __name__ :
    app.run()
