## 这是一个基于WSGI协议实现的小型web服务器及web框架demo

	以 python3 myserver.py 8001 webFrame:app 方式运行服务器；需要安转pymysql模块才能连接数据库；
	运行后，可以用浏览器发送请求http://localhost:8001/index.html

<h3>WSGI简介</h3>

<pre>
	WSGI可以实现web服务器与web框架的解耦，web服务器必须具备WSGI接口，所有的现代Python Web框架都已具备WSGI接口，它让你不对代码作修改就能使服务器和特点的web框架协同工作。
	WSGI接口定义非常简单，它只要求Web开发者实现一个函数，就可以响应HTTP请求。下面是最简单的Web版本的“Hello World!”：

	def application(environ, start_response):
    	start_response('200 OK', [('Content-Type', 'text/html')])
    	return 'Hello World!'
	上面的application()函数就是符合WSGI标准的一个HTTP处理函数，它接收两个参数：
		environ：一个包含所有HTTP请求信息的dict对象；
		start_response：一个发送HTTP响应的函数。
	整个application()函数本身没有涉及到任何解析HTTP的部分，也就是说，把底层web服务器解析部分和应用程序逻辑部分进行了分离，这样开发者就可以专心做一个领域了，不过，等等，这个application()函数怎么调用？如果我们自己调用，两个参数environ和start_response我们没法提供，返回的str也没法发给浏览器。
	所以application()函数必须由WSGI服务器来调用。
</pre>

<h3>文档目录</h3>
<pre>
├── dynamic
│   └── webFrame.py  # web框架文件
├── myserver.py   # web服务器文件
├── static # 静态资源文件
│   ├── css
│   │   ├── bootstrap.min.css
│   │   ├── main.css
│   │   └── swiper.min.css
│   └── js
│       ├── bootstrap.min.js
│       ├── jquery-1.12.4.js
│       ├── jquery-1.12.4.min.js
│       ├── jquery.animate-colors.js
│       ├── jquery.animate-colors-min.js
│       ├── jquery.cookie.js
│       ├── jquery-ui.min.js
│       ├── server.js
│       ├── swiper.jquery.min.js
│       ├── swiper.min.js
│       └── zepto.min.js
├── stock_db.sql # 数据库文件
└── templates # 模板资源文件
    ├── center.html
    ├── index.html
    └── update.html
</pre>

