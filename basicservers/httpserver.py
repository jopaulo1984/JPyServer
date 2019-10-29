"""
Basic HTTP/1.1 Server
=====================

Author: Joao Paulo F Silva
"""
from .tcpserver import TCPServer

class HTTPServer(TCPServer):   
    METHODS = ("GET", "POST", "HEAD", "PUT", "OPTIONS", "DELETE", "TRACE", "CONNECT")
    
    def __init__(self, port=80, onreceived=None):
        super().__init__(port)
        self.__content = dict()
        self.onreceived = onreceived
    
    @property
    def onreceived(self):        
        return self.__on_rcvd
    
    @onreceived.setter
    def onreceived(self, callback):
        if callback is not None and not callable(callback):
            raise Exception("'{}' não é uma função.".format(str(callback)))        
        self.__on_rcvd = callback

    def __get_content(self, rcvmsg):        
        _max = len(rcvmsg)        
        def __doerror():
            raise Exception("A mensagem recebida não obedece ao protocolo HTTP.")
        
        def __estd7(result, index):
            result["content"] = (rcvmsg[index:]).encode()
            return result
        
        def __estd5(result, index, key):
            i = index
            acc = ""            
            while i < _max and rcvmsg[i] == " ":
                i += 1                
            while i < _max:                
                if rcvmsg[i] == "\r":
                    result["header"][key] = acc
                    return __estd3(result, i + 1)                
                acc += rcvmsg[i]                
                i += 1
            return result
        
        def __estd3(result, index):
            i = index
            acc = ""            
            while i < _max and rcvmsg[i] != '\n':
                i += 1            
            i += 1
            while i < _max:
                if rcvmsg[i] == "\n":
                    return __estd7(result, i + 1)                    
                if rcvmsg[i] == ":":
                    return __estd5(result, i + 1, acc)                
                acc += rcvmsg[i]                
                i += 1
            return result
        
        def __estd2(result, index):
            i = index
            acc = ""
            while i < _max:                
                if rcvmsg[i] == " ":
                    result["file"] += acc
                    return __estd3(result, i + 1)                
                if rcvmsg[i] in ('\r','\n'):
                    __doerror()                
                acc += rcvmsg[i]                
                i += 1
            return result
        
        def __estd1(result, index):
            i = index
            while i < _max:
                if rcvmsg[i] != ' ':                                       
                    if rcvmsg[i] == '/' or (result['method'] == "OPTIONS" and rcvmsg[i] == '*'):
                        result['file'] = rcvmsg[i]
                        return __estd2(result, i + 1)                    
                    __doerror()                    
                i += 1                
            return result
        
        def __estd0(result, index):
            i = index
            acc = ""
            while i < _max:
                if rcvmsg[i] == " ":
                    if acc in self.METHODS:
                        result["method"] = acc
                        return __estd1(result, i + 1)                    
                    __doerror()                    
                else:
                    acc += rcvmsg[i]                    
                i += 1                
            return result
                
        return __estd0({"method":"","file":"","header":{},"content":b""}, 0)         

    def received(self, conn, content):
        """Overload this function to get the content received by the TCP server.
        If this function is overloaded, the onreceived event will not be automatically submitted.""" 
        if callable(self.onreceived):
            try:
                self.__content[conn] = self.__get_content(content.decode())
            except Exception as ex:
                print(ex)
                return                
            #print("Content: " + str(content) + "\nConnection: " + str(conn) + "\nFile: " + str(self.__content[conn]["file"]) + "\n")
            if self.__content[conn]['method'] == "TRACE":
                self.send_response(conn, "200 OK", self.__content[conn]["header"], self.__content[conn]["content"])
            else:
                self.onreceived(self, conn, self.__content.pop(conn))
            #self.__content.pop(conn)

    def send_response(self,conn,code,header={},content=b''):
        """
        Send an answer to the client.
        
        ========= ======================================================
        Parameter Description
        --------- ------------------------------------------------------
        conn      TCP connection.
        code      HTTP response code.
        header    dictionary containing the HTTP protocol header.
        content   bytes containing the message to be sent to the client.
        ========= ======================================================
        
        """
        h = ""
        for key in header.keys():
            h += "%s: %s\r\n" % (key,header[key])
        res = b"HTTP/1.1 %s\r\n%sContent-Length: %i\n\r\n%s" % (code.encode(),h.encode(),len(content),content)
        conn.send(res)
    
    def http_date(self, date):
        """"""
        return date.strftime('%a, %d %b %Y %I:%M:%S %p GMT')
    
    def http_date_now(self):
        """"""
        import datetime
        return self.http_date(datetime.datetime.now())
#
