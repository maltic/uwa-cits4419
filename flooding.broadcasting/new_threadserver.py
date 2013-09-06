import socket,select

def broadcast_data(sock,message):
    for socket in conn_list:
        if socket != s and socket !=sock:
            try:
                socket.send(message)
            except:
                socket.close()
                conn_list.remove(socket)

if __name__ == "__main__":
    conn_list = []
    receive_buffer = 4096
    port = 8000

    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    s.bind(("0.0.0.0",port))
    s.listen(10)

    conn_list.append(s)

    print "Server started on port "+str(port)

    while 1:
        read_sockets,write_sockets,error_sockets=select.select(conn_list,[],[])

        for sock in read_sockets:
            if sock == s:
                sockfd,addr=s.accept()
                conn_list.append(sockfd)
                print "Client (%s, %s) connected" % addr

                broadcast_data(sockfd, "[%s:%s] is online\n" %addr)

            else:
                try:
                    data=sock.recv(receive_buffer)
                    if data:
                        broadcast_data(sock,"\r"+'<'+str(sock.getpeername())+'>'+data)
                except:
                    broadcast_data(sock,"Client (%s, %s) is offline" % addr)
                    print "Client (%s, %s) is offline" % addr
                    sock.close()
                    conn_list.remove(sock)
                    continue
    s.close()
