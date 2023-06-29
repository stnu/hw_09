import os
import socket
from http import HTTPStatus


def get_open_port():
    with socket.socket() as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    srv_addr = ('127.0.0.1', get_open_port())
    print(f'Starting on {srv_addr}, pid: {os.getpid()}')

    s.bind(srv_addr)
    s.listen(1)

    while True:
        print("Waiting for a connection...")
        conn, baddr = s.accept()
        print('Connection from: ', baddr)

        recv_bytes = conn.recv(1024)
        text = recv_bytes.decode('utf-8')

        method_from_request = text.split(" /")[0]
        headers_from_request = text.split("\r\n")[1:]
        sub_str_with_status = text.split("\r\n")[0]
        try:
            status_from_request = int(sub_str_with_status.split(" ")[1].split("status=")[1])
            status = HTTPStatus(status_from_request)
        except:
            status = HTTPStatus(200)

        body = f"<div>Request Method: {method_from_request}</div>" \
               f"<div>Request Source: {srv_addr}</div>" \
               f"<div>Response Status: {status.value} {status.name}</div>" \
               f"<br></br>"
        for item in headers_from_request:
            body += f"<div>{item}</div>"

        status_line = f"HTTP/1.1 {status.value} {status.name}"
        headers = '\r\n'.join([
            status_line,
            f'Content-Length: {len(body)}',
            'Content-Type: text/html'
        ])

        resp = '\r\n\r\n'.join([
            headers,
            body
        ])

        conn.send(resp.encode('utf-8'))
        conn.close()
