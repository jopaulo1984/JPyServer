"""
Basic TCP Server
================

Author: Joao Paulo F Silva
"""
import socket
import _thread
import os

class TCPServer:
    STOPPED  = 0
    STOPPING = 1
    RUNNING  = 2
    
    def __init__(self, port=80):
        self.__port = port
        self.__tcp = None
        self.__state = TCPServer.STOPPED
        
    def __new_thread_of_connection(self, tcpconn):
        con, cliente = tcpconn        
        msgrcv = b""
        con.settimeout(0.2)
        while True:
            try:
                msg = con.recv(1024)
            except:
                break
            if not msg: break
            msgrcv += msg
        #print(msgrcv)
        self.received(con, msgrcv)
        con.close()
            
    def received(self, conn, content):
        """Overload this function to get the content received by the TCP server.""" 
        pass
    
    def main(self):
        """Function that contains the main loop.
        At each connection, a thread is generated. By the thread, 
        the received function is invoked by passing the connection 
        and the content sent by the client as function parameters."""
        if self.__state == TCPServer.RUNNING:
            return
        self.__tcp = tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            tcp.bind(("", self.__port))
        except Exception as ex:
            self.__tcp = None
            raise ex
        
        tcp.listen(10)
        self.__state = TCPServer.RUNNING
        
        while self.__state == TCPServer.RUNNING:
            try:
                con, cliente = tcp.accept()
                _thread.start_new_thread(self.__new_thread_of_connection,((con,cliente),))
            except:
                pass
            
        self.__state = TCPServer.STOPPED
    
    def close(self):
        """Close all connections."""
        self.__close = True
        if self.__tcp :
            try:
                self.__state = TCPServer.STOPPING
                self.__tcp.shutdown(socket.SHUT_RDWR)
                self.__tcp.close()
                while self.__state != TCPServer.STOPPED: pass
            except Exception as ex:
                pass
        self.__tcp = None
#

