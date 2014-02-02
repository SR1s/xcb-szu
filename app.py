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
        sql = """SELECT `id`, `title` FROM `columns` 
                WHERE `is_delete` <> 1 ORDER BY `order`; """
        cursor = g.db.cursor()
        cursor.execute(sql)
        columns = [dict(id=column[0], title=column[1]) for column in cursor.fetchall()]
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
    sql = """SELECT `id`, `title` FROM `columns` 
            WHERE `is_delete` <> 1 ORDER BY `order`; """
    cursor = g.db.cursor()
    cursor.execute(sql)
    columns = [dict(id=column[0], title=column[1]) for column in cursor.fetchall()]
    return render_template("admin/column.html", column="active", columns=columns)

@app.route('/admin/column/add', methods=['POST'])
def admin_column_add():
    sql = """INSERT INTO `columns` (`title`) VALUES ( %s ); """
    if request.method == 'POST' :
        title = request.form['title']
        cursor = g.db.cursor()
        cursor.execute(sql, (title,))
        g.db.commit()
    return redirect(url_for("admin_column"))

@app.route('/admin/column/del/<int:id>')
def admin_column_del():
    sql = """INSERT INTO `columns` (`title`) VALUES ( %s ); """
    return redirect(url_for("admin_column"))



@app.route('/admin/content')
def admin_content():
    return render_template("admin/basic.html", content="active")

@app.route('/admin/form')
def admin_index():
    return render_template("admin/basic.html", form="active")

if "__main__" == __name__ :
    app.run()
