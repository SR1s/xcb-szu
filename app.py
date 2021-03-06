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
                 WHERE `is_delete` = 0 
                 AND `parent_id` = 0
                 ORDER BY `order`; """
        cursor = g.db.cursor()
        cursor.execute(sql)
        columns = [dict(id=column[0], title=column[1]) 
                        for column in cursor.fetchall()]
        return columns
    return dict(get_menu=get_menu)

@app.context_processor
def get_all_columns():
    def get_all_columns():
        sql_parent = """SELECT `id`, `title` 
                        FROM `columns` 
                        WHERE `is_delete` = 0 
                        AND `parent_id` = 0
                        ORDER BY `order`; """

        sql_child = """SELECT `id`, `title` 
                       FROM `columns` 
                       WHERE `is_delete` = 0 
                       AND `parent_id` = %s 
                       ORDER BY `order`; """
        cursor = g.db.cursor()
        cursor.execute(sql_parent)
        columns = [dict(id=column[0], title=column[1]) 
                        for column in cursor.fetchall()]
        for column in columns :
            cursor.execute(sql_child, (column["id"],))
            column["child"] = [dict(id=col[0], title=col[1])
                            for col in cursor.fetchall() ]
        return columns
    return dict(get_all_columns=get_all_columns)


### to be done
@app.context_processor
def get_columns():
    def get_columns():
        sql = """SELECT `id`, `title` 
                 FROM `columns` 
                 WHERE `is_delete` <> 1 
                 ORDER BY `order`; """
        cursor = g.db.cursor()
        cursor.execute(sql)
        columns = [dict(id=column[0], title=column[1]) 
                        for column in cursor.fetchall()]
        return columns
    return dict(get_columns=get_columns)

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

@app.route('/column/<int:post_id>')
def column(post_id):
    sql = """SELECT `id` 
             FROM `columns` 
             WHERE `parent_id` = %s
             AND `is_delete` = 0 
             ORDER BY `order`;"""
    cursor = g.db.cursor()
    cursor.execute(sql, (post_id,))
    sub_id = cursor.fetchall()[0][0]
    return redirect(url_for("column_sub", post_id=post_id, sub_id=sub_id))

@app.route('/column/<int:post_id>/sub/<int:sub_id>')
def column_sub(post_id, sub_id):
    sql_search_cur_big = """SELECT `id`, `title` 
                            FROM `columns` 
                            WHERE `id` = %s 
                            AND `is_delete` = 0;"""
    sql_search_sub_cols = """SELECT `id`, `title` 
                             FROM `columns` 
                             WHERE `parent_id` = %s
                             AND `is_delete` = 0 
                             ORDER BY `order` ;"""
    sql_search_content = """SELECT `id`, `title`, `time` 
                            FROM `contents` 
                            WHERE `is_delete` = 0 
                            AND `column_id` = %s 
                            ORDER BY `time` desc;"""
    cursor = g.db.cursor()
    cursor.execute(sql_search_cur_big, (post_id,))
    cur_big=dict()
    result = cursor.fetchall()
    cur_big["id"] = result[0][0]
    cur_big["title"] = result[0][1]

    cursor.execute(sql_search_sub_cols,(post_id,))
    columns = [dict(id=column[0], title=column[1]) 
               for column in cursor.fetchall() ]
    for column in columns:
        if column['id'] == sub_id:
            cur_sub = column
            break
    cursor.execute(sql_search_content,(sub_id,))
    contents = [dict(id=content[0], title=content[1], time=content[2]) 
                for content in cursor.fetchall() ]
    return render_template("column-sub.html", id=post_id, columns=columns,
                        cur_big=cur_big, cur_sub=cur_sub, contents=contents )

@app.route("/content/<int:post_id>")
def content(post_id):
    sql = """SELECT `title`, `content`, `column_id`, `time` 
             FROM `contents` 
             WHERE `id` = %s 
             AND `is_delete` = 0; """
    cursor = g.db.cursor()
    cursor.execute(sql, (post_id))
    contents = [dict(title=con[0], content=con[1], 
                    column_id=con[2], time=con[3]) 
               for con in cursor.fetchall() ][0]
    
    sql_parent_id = """SELECT `parent_id` 
                       FROM `columns` 
                       WHERE `id` = %s;"""
    cursor.execute(sql_parent_id,(contents["column_id"],))
    parent_id = cursor.fetchall()[0][0]


    sql_search_cur_big = """SELECT `id`, `title` 
                            FROM `columns` 
                            WHERE `id` = %s 
                            AND `is_delete` = 0;"""
    cursor.execute(sql_search_cur_big, (parent_id,))
    cur_big=dict()
    result = cursor.fetchall()
    cur_big["id"] = result[0][0]
    cur_big["title"] = result[0][1]

    sql_search_sub_cols = """SELECT `id`, `title` 
                             FROM `columns` 
                             WHERE `parent_id` = %s
                             AND `is_delete` = 0 
                             ORDER BY `order` ;"""
    cursor.execute(sql_search_sub_cols,(parent_id,))
    columns = [dict(id=column[0], title=column[1]) 
               for column in cursor.fetchall() ]

    for column in columns:
        if column['id'] == contents["column_id"]:
            cur_sub = column
            break
    return render_template("content.html", id=parent_id, columns=columns,
                        cur_big=cur_big, cur_sub=cur_sub, contents=contents )

@app.route('/apply/report_outter', methods=['POST','GET'])
def report_outter():
    if request.method == "POST" :
        sql = """INSERT INTO `report-outer` 
                 (`content`,  `units`,  `leaders`, 
                  `sections`, `date`,   `place`, 
                  `linkman`,  `phone`,  `note`) 
                 VALUES ( %s, %s, %s, 
                          %s, %s, %s, 
                          %s, %s, %s ); """
        cursor   = g.db.cursor()
        content  = request.form['content']
        units    = request.form['units']
        leaders  = request.form['leaders']
        sections = request.form['sections']
        date     = request.form['date']
        place    = request.form['place']
        linkman  = request.form['linkman']
        phone    = request.form['phone']
        note     = request.form.get('note', default=" ")
        cursor.execute(sql, (content,  units, leaders,
                             sections, date,  place, 
                             linkman,  phone, note ))
        g.db.commit()
        return redirect(url_for("report_outter_status"))
    return render_template("report-outter.html", report_outter="now")

@app.route('/apply/report_inner', methods=['POST','GET'])
def report_inner():
    if request.method == "POST" :
        sql = """INSERT INTO `report-inner` 
                 (`content`,  `units`,  `leaders`, 
                  `sections`, `date`,   `place`, 
                  `linkman`,  `phone`,  `note`) 
                 VALUES ( %s, %s, %s, 
                          %s, %s, %s, 
                          %s, %s, %s ); """
        cursor   = g.db.cursor()
        content  = request.form['content']
        units    = request.form['units']
        leaders  = request.form['leaders']
        sections = request.form['sections']
        date     = request.form['date']
        place    = request.form['place']
        linkman  = request.form['linkman']
        phone    = request.form['phone']
        note     = request.form.get('note', default=" ")
        cursor.execute(sql, (content,  units, leaders,
                             sections, date,  place, 
                             linkman,  phone, note ))
        g.db.commit()
        return redirect(url_for("report_inner_status"))
    return render_template("report-inner.html", report_inner="now")

@app.route('/apply/report_outter/status')
def report_outter_status():
    sql = """SELECT `id`, `content`, `date`, 
                    `linkman`, `status`, `time`
             FROM `report-outer` 
             WHERE `is_delete` = 0 ;"""
    cursor = g.db.cursor()
    cursor.execute(sql)
    status_map = dict()
    status_map[-1] = "申请不通过"
    status_map[0 ] = "申请中" 
    status_map[1 ] = "申请通过"
    status = [dict(id=statu[0],   content=statu[1], 
                   date=statu[2], linkman=statu[2], 
                   status=status_map[statu[4]], 
                   time=statu[5] )    
              for statu in cursor.fetchall() ]
    return render_template("report-outter-status.html", report_outter="now", 
                           status=status)

@app.route('/apply/propaganda')
def propaganda():
    return render_template("propaganda.html", propaganda="now")

@app.route('/apply/contribute')
def contribute():
    return render_template("contribute.html", contribute="now")

@app.route('/apply/report_inner/status')
def report_inner_status():
    sql = """SELECT `id`, `content`, `date`, 
                    `linkman`, `status`, `time`
             FROM `report-inner` 
             WHERE `is_delete` = 0 ;"""
    cursor = g.db.cursor()
    cursor.execute(sql)
    status_map = dict()
    status_map[-1] = "申请不通过"
    status_map[0 ] = "申请中" 
    status_map[1 ] = "申请通过"
    status = [dict(id=statu[0],   content=statu[1], 
                   date=statu[2], linkman=statu[2], 
                   status=status_map[statu[4]], 
                   time=statu[5] )    
              for statu in cursor.fetchall() ]
    return render_template("report-inner-status.html", report_inner="now", 
                           status=status)


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
                    WHERE `is_delete` = 0 
                    AND `parent_id` = 0 ;"""
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
             WHERE `id` = %s;"""
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


@app.route("/admin/column/<int:post_id>")
def admin_sub_column(post_id):
    sql = """SELECT `id`, `title`, `parent_id`
             FROM `columns`
             WHERE `is_delete` <> 1
             AND `parent_id` = %s 
             ORDER BY `order`;"""
    cursor = g.db.cursor()
    cursor.execute(sql, (post_id,))
    columns = [dict(id=column[0], title=column[1], parent_id=column[2])
               for column in cursor.fetchall()]

    sql = """SELECT `title`
             FROM `columns`
             WHERE `is_delete` <> 1
             AND `id` = %s ;"""
    cursor.execute(sql, (post_id,))
    title = cursor.fetchall()[0][0]
    return render_template('admin/column-sub.html', 
            column="active", columns=columns, 
            id=post_id, title = title)

@app.route('/admin/column/<int:post_id>/add', methods=['POST'])
def admin_sub_column_add(post_id):
    sql_search = """SELECT MAX(`id`) 
                    FROM `columns` 
                    WHERE `is_delete` = 0 
                    AND `parent_id` = %s ;"""
    sql = """INSERT INTO `columns` (`title`, `order`, `parent_id`) 
             VALUES ( %s, %s, %s ); """
    if request.method == 'POST' :
        title = request.form['title']
        cursor = g.db.cursor()
        cursor.execute(sql_search, (post_id, ))
        max_id = cursor.fetchall()[0][0]
        if max_id:
            max_id = max_id + 1
        else :
            max_id = 1
        cursor.execute(sql, (title, max_id, post_id))
        g.db.commit()
    return redirect(url_for("admin_sub_column", post_id=post_id))

@app.route('/admin/column/<int:post_id>/del/<int:del_id>')
def admin_column_del(post_id, del_id):
    sql = """UPDATE `columns` 
             SET `is_delete` =  '1' 
             WHERE `id` = %s;"""
    cursor = g.db.cursor()
    cursor.execute(sql, (del_id, ))
    g.db.commit()
    return redirect(url_for("admin_sub_column",
                    post_id=post_id))

@app.route('/admin/column/<int:post_id>/up/<int:up_id>')
def admin_sub_column_up(post_id, up_id):
    sql_search = """SELECT `id`, `order` FROM `columns` 
                    WHERE `is_delete` <> 1
                    AND `parent_id` = %s
                    ORDER BY `order`; """
    sql_update = """UPDATE `columns`
                    SET `order` = %s 
                    WHERE `id` = %s;"""
    cursor = g.db.cursor()
    cursor.execute(sql_search, (post_id,))
    columns = list(cursor.fetchall())
    column_pre_id = up_id
    column_pre_order = None
    column_now_order = None
    for column in columns:
        if column[0] != up_id:
            column_pre_id = column[0]
            column_pre_order = column[1]
        else :
            column_now_id = column[0]
            column_now_order = column[1]
            break
    #return sql_update % (column_pre_order, up_id) + '<br/>' + sql_update % (column_now_order, column_pre_id)
    if column_now_order and column_pre_order :
        cursor.execute(sql_update, (column_pre_order, up_id))
        cursor.execute(sql_update, (column_now_order, column_pre_id))
        g.db.commit()
    return redirect(url_for("admin_sub_column",post_id=post_id))


@app.route('/admin/column/<int:post_id>/down/<int:down_id>')
def admin_sub_column_down(post_id, down_id):
    sql_search = """SELECT `id`, `order` FROM `columns` 
                    WHERE `is_delete` <> 1
                    AND `parent_id` = %s
                    ORDER BY `order` desc ; """
    sql_update = """UPDATE `columns`
                    SET `order` = %s 
                    WHERE `id` = %s;"""
    cursor = g.db.cursor()
    cursor.execute(sql_search, (post_id,))
    columns = list(cursor.fetchall())
    column_pre_id = down_id
    column_pre_order = None
    column_now_order = None
    for column in columns:
        if column[0] != down_id:
            column_pre_id = column[0]
            column_pre_order = column[1]
        else :
            column_now_id = column[0]
            column_now_order = column[1]
            break
    #return sql_update % (column_pre_order, down_id) + '<br/>' + sql_update % (column_now_order, column_pre_id)
    if column_now_order and column_pre_order :
        cursor.execute(sql_update, (column_pre_order, down_id))
        cursor.execute(sql_update, (column_now_order, column_pre_id))
        g.db.commit()
    return redirect(url_for("admin_sub_column",post_id=post_id))



###############################
#
# content management
#
###############################

@app.route('/admin/content')
def admin_content():
    sql = """SELECT `id`, `title`, `time` 
             FROM `contents` 
             WHERE `is_delete` = 0
             ORDER BY `time` desc ;"""
    cursor = g.db.cursor()
    cursor.execute(sql)
    contents = [dict(id=content[0], title=content[1], 
                     time=content[2]) 
                     for content in cursor.fetchall()]
    return render_template("admin/content.html", 
            contents=contents, content="active")

@app.route("/admin/content/add", methods=['POST','GET'])
def admin_content_add():
    if request.method == 'POST':
        sql = """INSERT INTO `contents`(`title`, `content`, `column_id`) 
                 VALUES (%s, %s, %s); """
        cursor = g.db.cursor()
        title = request.form['title']
        content = request.form['content']
        column_id = request.form['column_id']
        cursor.execute(sql, (title, content, column_id))
        g.db.commit()
        return redirect(url_for("index"))
    return render_template("admin/content-edit.html")

@app.route("/admin/content/edit/<int:post_id>", methods=['GET','POST'])
def admin_content_edit(post_id):
    sql = """SELECT `title`, `content`, `column_id` 
             FROM `contents` 
             WHERE `id` = %s; """
    cursor = g.db.cursor()
    if request.method == "POST":
        sql = """UPDATE `contents` 
                 SET `title` = %s, 
                     `content` = %s, 
                     `column_id` = %s 
                 WHERE `id` = %s ;"""
        title = request.form['title']
        content = request.form['content']
        column_id = request.form['column_id']
        cursor.execute(sql, (title, content, column_id, post_id))
        g.db.commit()
        return redirect(url_for("admin_content"))
    cursor.execute(sql, (post_id,))
    content=dict()
    for con in cursor.fetchall():
        content["title"] = con[0]
        content["content"] = con[1]
        content["column_id"] = con[2]
    return render_template("admin/content-edit.html", content = content)

@app.route("/admin/content/del/<int:post_id>", methods=['GET',])
def admin_content_del(post_id):
    sql = """UPDATE `contents` 
             SET `is_delete` = 1
             WHERE `id` = %s; """
    cursor = g.db.cursor()
    cursor.execute(sql, (post_id,))
    g.db.commit()
    return redirect(url_for("admin_content"))


###############################
#
# form management
#
###############################

@app.route('/admin/form/report-outter')
def admin_report_outter():
    sql = """SELECT `id`, `content`, `date`, 
                    `linkman`, `time`
             FROM `report-outer` 
             WHERE `is_delete` = 0 
             AND `status` = 0;"""
    cursor = g.db.cursor()
    cursor.execute(sql)
    status_map = dict()
    status_map[-1] = "申请不通过"
    status_map[0 ] = "申请中" 
    status_map[1 ] = "申请通过"
    status = [dict(id=statu[0],   content=statu[1], 
                   date=statu[2], linkman=statu[2], 
                   time=statu[4] )    
              for statu in cursor.fetchall() ]
    return render_template("/admin/report-outter.html", 
                           status=status)

@app.route('/admin/form/report-inner')
def admin_report_inner():
    sql = """SELECT `id`, `content`, `date`, 
                    `linkman`, `time`
             FROM `report-inner` 
             WHERE `is_delete` = 0 
             AND `status` = 0;"""
    cursor = g.db.cursor()
    cursor.execute(sql)
    status_map = dict()
    status_map[-1] = "申请不通过"
    status_map[0 ] = "申请中" 
    status_map[1 ] = "申请通过"
    status = [dict(id=statu[0],   content=statu[1], 
                   date=statu[2], linkman=statu[2], 
                   time=statu[4] )    
              for statu in cursor.fetchall() ]
    return render_template("/admin/report-inner.html",
                           report_inner="now",
                           status=status)

@app.route("/admin/form/report-outter-pass/<int:post_id>")
def admin_report_outter_pass(post_id):
    sql = """UPDATE `report-outer` 
             SET `status` = 1 
             WHERE `id` = %s; """
    cursor = g.db.cursor()
    cursor.execute(sql, (post_id,))
    g.db.commit()
    return redirect(url_for("admin_report_outter"))

@app.route("/admin/form/report-inner-pass/<int:post_id>")
def admin_report_inner_pass(post_id):
    sql = """UPDATE `report-inner` 
             SET `status` = 1 
             WHERE `id` = %s; """
    cursor = g.db.cursor()
    cursor.execute(sql, (post_id,))
    g.db.commit()
    return redirect(url_for("admin_report_inner"))

@app.route("/admin/form/report-outter-unpass/<int:post_id>")
def admin_report_outter_pass(post_id):
    sql = """UPDATE `report-outer` 
             SET `status` = -1 
             WHERE `id` = %s; """
    cursor = g.db.cursor()
    cursor.execute(sql, (post_id,))
    g.db.commit()
    return redirect(url_for("admin_report_outter"))

@app.route("/admin/form/report-inner-unpass/<int:post_id>")
def admin_report_inner_pass(post_id):
    sql = """UPDATE `report-inner` 
             SET `status` = -1 
             WHERE `id` = %s; """
    cursor = g.db.cursor()
    cursor.execute(sql, (post_id,))
    g.db.commit()
    return redirect(url_for("admin_report_inner"))

@app.route("/admin/form/report-inner-detail/<int:post_id>")
def admin_report_inner_detail(post_id):
    sql = """SELECT `content`,  `units`,  `leaders`, 
                    `sections`, `date`,   `place`, 
                    `linkman`,  `phone`,  `note` 
             FROM `report-inner` 
             WHERE `is_delete` = 0 
             AND `id` = %s ; """
    cursor = g.db.cursor()
    cursor.execute(sql, (post_id,))
    result = cursor.fetchall()[0]
    statu = dict()
    statu['content']  = result[0]
    statu['units']    = result[1]
    statu['leaders']  = result[2]
    statu['sections'] = result[3]
    statu['date']     = result[4]
    statu['place']    = result[5]
    statu['linkman']  = result[6]
    statu['phone']    = result[7]
    statu['note']     = result[8]
    return render_template("report-inner-detail.html",
                            report_inner="now", 
                            statu = statu)


@app.route("/admin/form/report-outter-detail/<int:post_id>")
def admin_report_outter_detail(post_id):
    sql = """SELECT `content`,  `units`,  `leaders`, 
                    `sections`, `date`,   `place`, 
                    `linkman`,  `phone`,  `note` 
             FROM `report-outer` 
             WHERE `is_delete` = 0 
             AND `id` = %s ; """
    cursor = g.db.cursor()
    cursor.execute(sql, (post_id,))
    result = cursor.fetchall()[0]
    statu = dict()
    statu['content']  = result[0]
    statu['units']    = result[1]
    statu['leaders']  = result[2]
    statu['sections'] = result[3]
    statu['date']     = result[4]
    statu['place']    = result[5]
    statu['linkman']  = result[6]
    statu['phone']    = result[7]
    statu['note']     = result[8]
    return render_template("report-outter-detail.html",
                            report_outter="now", 
                            statu = statu)

@app.route('/admin/form')
def admin_index():
    return render_template("admin/basic.html", form="active")

if "__main__" == __name__ :
    app.run(host="0.0.0.0")
