import time
import re
from pymysql import *
import urllib.parse

# 模板文件路径
tem_dir = "./templates"

# 路由,请求的资源路径与相应的处理方法相对应列表
g_path_func = {}


# 装饰器  当定义index 方法的时候 就能够自动完成 r"/index\.html" 和 index方法的对应
def route(path):
    def w(func):
        g_path_func[path] = func
        def call_fun():
            func()

        return call_fun

    return w


@route(r"/index\.html")
def index(file_path, pattern=None):
    """处理/index.html请求资源"""
    try:
        f = open(tem_dir + file_path)
    except Exception as ret:
        print("-----------index.html--error------")
        return "index index error ,current time "
    else:
        cont = f.read()
        f.close()
        # 从数据库获取数据
        conn = connect(host="localhost", port=3306, database="stock_db", user="root", passwd="mysql", charset="utf8")
        cur = conn.cursor()
        sql = "select * from info"
        count = cur.execute(sql)
        result = cur.fetchall()

        cur.close()
        conn.close()

        template = """
            <tr>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td><input type="button" value="添加" id="toAdd" name="toAdd" systemidvaule="%s"></td>
            </tr>
        """
        html = ""
        for item in result:
            html += (template % (item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[1]))
        # 替换掉模板文件中需要显示数据库数据的部分内容
        cont = re.sub(r"\{.*\}", html, cont)
        return cont


@route(r"/update/(\d+).html")
def update_func(filepath, pattern=None):
    try:
        # print("-----------", tem_dir + "update.html")
        f = open(tem_dir + "/update.html")
    except Exception as ret:
        return "-----read------update.html--error------ "
    else:

        cont = f.read()
        f.close()
        # 从数据库获取数据
        ret = re.match(pattern, filepath)
        info_code = ret.group(1)

        # 根据股票代码获取focus 的 note_info
        conn = connect(host="localhost", port=3306, database="stock_db", user="root", passwd="mysql", charset="utf8")
        cur = conn.cursor()
        sql = "select note_info from focus where info_id = (select id from info where code = %s)" % info_code
        count = cur.execute(sql)
        note_info = cur.fetchone()
        note_info = note_info[0]
        cur.close()
        conn.close()
        cont = re.sub(r"\{%code%\}", info_code, cont)
        cont = re.sub(r"\{%note_info%\}", note_info, cont)

        return cont


@route(r"/update/(\d*)/(.*)\.html")
def update_note_info(file_path, pattern=None):

    # 提取 股票编码 以及修改的note_info 信息
    ret = re.match(pattern, file_path)
    info_code = ret.group(1)
    note_info = ret.group(2)

    #  60%20hehe 处理修改内容中的空格问题
    # 请求内容作为路径参数传递，不能有空格
    note_info = urllib.parse.unquote(note_info)

    # 数据库链接
    conn = connect(host="localhost", port=3306, database="stock_db", user="root", passwd="mysql", charset="utf8")
    cur = conn.cursor()
    # 根据股票代码，获取info 表中的id,在根据id 修改focus 中note_info信息
    sql = "update focus set note_info=%s where info_id = (select id from info where code = %s)"
    count = cur.execute(sql, [note_info, info_code])
    conn.commit()
    cur.close()
    conn.close()
    if count > 0:
        return "修改 ok"
    else:
        return "修改 fail"





@route(r"/del/(\d+).html")
def del_func(filepath, pattern=None):
    """取消关注功能模块"""
    ret = re.match(pattern, filepath)
    # 获取关注的股票代码
    info_code = ret.group(1)

    # 数据库链接
    conn = connect(host="localhost", port=3306, database="stock_db", user="root", passwd="mysql", charset="utf8")
    cur = conn.cursor()
    # 根据股票代码，在focus表中删除相应数据
    sql = "delete from focus where info_id = (select id from info where code = %s)"% info_code
    count = cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()
    if count > 0:
        return "取消关注ok,股票代码：%s" % info_code
    else:
        return "取消关注fail,股票代码：%s" % info_code


@route(r"/add/(\d+).html")
def add(filepath, pattern=None):
    """ 添加关注功能代码"""
    ret = re.match(pattern, filepath)

    # 获取关注的股票代码
    info_code = ret.group(1)

    # 根据获取到的股票代码查询是否已经关注，如果关注了，就提示已经关注
    # 如果没有关注，则将相应的信息插入到focus表，并提示关注成功

    conn = connect(host="localhost", port=3306, database="stock_db", user="root", passwd="mysql", charset="utf8")
    cur = conn.cursor()


    sql = "select * from focus where info_id = (select id from info where code = %s)"

    count = cur.execute(sql, [info_code])

    if count > 0:
        return "已经关注了,不要重复关注,股票代码：%s" % info_code
    else:
        sql = "insert into focus (info_id) select id from info where code = %s "
        count = cur.execute(sql, [info_code])
        conn.commit()
        cur.close()
        conn.close()
        if count > 0:
            return "关注ok,股票代码：%s" % info_code
        else:
            return "关注fail,股票代码：%s" % info_code


@route(r"/center\.html")
def center(file_path, pattern=None):
    # 获取模板文件，将.py 替换为 .html
    # file_path = file_path.replace(".py", ".html")
    try:
        # print("-----------", tem_dir + file_path)
        f = open(tem_dir + file_path)
    except Exception as ret:
        print("-----------center.html--error------")
        return "-----read------center.html--error------ "
    else:
        cont = f.read()
        f.close()
        # 重数据库获取数据
        # 连接数据库
        conn = connect(host="localhost", port=3306, database="stock_db", user="root", passwd="mysql", charset="utf8")
        cur = conn.cursor()

        sql = "select i.code, i.short, i.chg, i.turnover, i.price, i.highs, f.note_info  from info as i inner join focus as f on i.id=f.info_id"

        count = cur.execute(sql)
        result = cur.fetchall()
        html_t = """
         <tr>
                       <td>%s</td>
                       <td>%s</td>
                       <td>%s</td>
                       <td>%s</td>
                       <td>%s</td>
                       <td>%s</td>
                       <td>%s</td>
                       <td>
                           <a type="button" class="btn btn-default btn-xs" href="/update/%s.html">
                           <span class="glyphicon glyphicon-star" aria-hidden="true"></span> 修改 </a>
                       </td>
                       <td>
                           <input type="button" value="删除" id="toDel" name="toDel" systemidvaule="%s">
                       </td>
                   </tr>

        """

        html = ""
        for item in result:
            html += (html_t % (item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[0], item[0],))

        cont = re.sub(r"\{.*\}", html, cont)
        cur.close()
        conn.close()
        return cont


def app(env, start_response):
    """实现了WSGI协议的接口，给web服务器调用"""
    status = "200 OK"
    response_headers = [("Content-Type", "text/html")]
    # 调用服务器的start_response方法，处理响应头
    start_response(status, response_headers)
    file_path = env["PATH_INFO"]

    # g_url_path = {
    #     r"/index\.html":index,
    #     r"/center\.html": center,
    #     r"/add\d*\.html": add,
    #  }
    # 正则规则 与路径匹配 ,则调用相应的方法
    for pattern, func in g_path_func.items():
        ret = re.match(pattern, file_path)

        if ret:
            return func(file_path, pattern)

    return "error ,not found " + file_path + ",current time :" + time.ctime()
