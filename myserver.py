from socket import *
import re
import threading
import sys


class WSGIServer():
    def __init__(self, path, port, app):
        # create socket
        self.server_sock = socket(AF_INET, SOCK_STREAM)
        # bind ip, port
        self.server_sock.bind(("", port))

        # listen
        self.server_sock.listen(200)

        # 模板文件路径
        self.g_html = path
        # web框架的WSGI接口
        self.app = app

        # 响应头
        self.res_headers = ""

    # http 响应函数
    def start_response(self, status, headers):
        """处理响应头.
            Args:
                status:响应状态码
                headers:响应头内容
        """
        self.res_headers = ""
        self.res_headers += ("HTTP/1.1 " + status + "\r\n")
        for item in headers:
            self.res_headers += "%s:%s\r\n" % (item[0], item[1])

    def handler_request(self, client_socket, recv_data):
        """
        处理接收到的数据
        :param client_socket: 处理客户端的socket
        :param recv_data: 客户端发送的数据
        :return:
        """
        header_line = recv_data.decode().splitlines()[0]
        # 解析请求文件路径
        file_path = re.match(r"\w+ (/.*) ", header_line).group(1)
        if file_path == "/":
            file_path = "/index.html"
            # 浏览器对.py 不是很友好，部分不能识别，故规定当客户请求的是.html时请求的是动态资源
        if file_path.endswith(".html"):
            env = {
                "PATH_INFO": file_path
            }
            # 将解析后要请求的信息给web框架处理
            response_body = self.app(env, self.start_response)
            if response_body is None:
                client_socket.close()
                return
            self.res_headers += "Content-Length : %d\r\n" % len(response_body.encode())
            self.res_headers += "\r\n"
            # 返回客户端请求的资源
            client_socket.send(self.res_headers.encode())
            client_socket.send(response_body.encode())
            # 关闭socket
            client_socket.close()

        else:
            file_path = self.g_html + file_path
            #处理请求静态资源，直接读取不经过web框架
            try:
                f = open(file_path, "rb")
                con = f.read()
                response_body = con
                response_headers = "HTTP/1.1 200 OK\r\n"
                response_headers += "Content-Length: %d\r\n" % len(response_body)
                response_headers += "\r\n"
            except:
                response_body = "sorry ,没有您请求的资源".encode()
                response_headers = "HTTP/1.1 404 Not Found\r\n"
                response_headers += "Content-Type: text/html; charset=utf-8\r\n"
                response_headers += "Content-Length: %d\r\n" % len(response_body)
                response_headers += "\r\n"
                print("-------static---error------", file_path)

            finally:
                client_socket.send(response_headers.encode())
                client_socket.send(response_body)
                client_socket.close()
                return

    def run_server(self):
        """开启服务器"""
        while True:
            # 等待client request
            client_socket, addr = self.server_sock.accept()

            # 接受客户端请求数据
            recv_data = client_socket.recv(2048)
            # 判断是否接受到数据
            if not recv_data:
                continue
            # 启用一个线程处理接收到的数据
            th = threading.Thread(target=self.handler_request, args=(client_socket, recv_data))
            th.start()


def main():
    if len(sys.argv) < 3:
        print("请以 python3 myserver.py 8888 webFrame:app 方式运行服务器")
        exit()
    else:
        g_dynamic_root = "./dynamic"  # web框架路径
        sys.path.append(g_dynamic_root)
        port = int(sys.argv[1])
        module_name = sys.argv[2].split(":")[0]
        app_name = sys.argv[2].split(":")[1]

        # 导入模块
        m = __import__(module_name)
        func_name = getattr(m, app_name)

    # 实例化服务对象
    ser = WSGIServer('./static', port, func_name)
    ser.run_server()

# python3 myserver.py 8001 webFrame:app

if __name__ == "__main__":
    main()
