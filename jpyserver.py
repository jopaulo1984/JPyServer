
from basicservers import HTTPServer
from fileinfo import File
from stdb.stdb import *
from datetime import datetime
import platform
import os
import json
import misc
import socket

global CONFIG
global SYSTEM

SYSTEM = {"host":socket.gethostbyname(socket.gethostname())}

try:
    with open("config.json", "r") as f:
        CONFIG = json.loads(f.read())
        f.close()
except:
    CONFIG = {
        "port":"80",
        "dir":"WWW",
        "name":"PyServer"
    }

if platform.system() == 'Linux': 
    SEPARATOR = r'/'
    EXEC = "python3 execute.py"
else:                            
    SEPARATOR = '\\'
    EXEC = "py execute.py"

class PyServer(HTTPServer):
    def __init__(self, inidir="www", name="PyServer", *args, **keyargs):
        super().__init__(*args, **keyargs)
        
        self.__inidir = inidir
        self.__name = name
        
        self.onreceived = self.__on_http_received
        
        self.__content_type = {
            "py"   :"text/html",
            "txt"  :"text/plain",
            "html" :"text/html; charset=utf-8",
            "js"   :"text/javascript",
            "png"  :"image/png",
            "jpeg" :"image/jpeg",
            "gif"  :"image/gif",
            "ico"  :"image/x-ico",
            "svg"  :"image/svg+xml",
            "json" :"application/json",
            "zip"  :"application/zip",
            "css"  :"text/css",
            "pdf"  :"application/pdf",
            "swf"  :"application/x-shockwave-flash"
            }
    
    def __compile_url(self, url):
        
        def __estd1(i, text, get):
            return misc.compile_keys_values(text[i:])
        
        def __estd0(i, text, get):
            
            f = ""
            
            while i < len(text):
                if text[i] == '?':
                    return f, __estd1(i + 1, text, get)
                else:
                    f += text[i]
                    i += 1
                    
            return f, get
        
        get = dict()
        
        return __estd0(0, url, get)
    
    def __on_http_received(self, http, tcpconn, content):
                
        f, get = self.__compile_url(content['file'])
        
        header = {"Date":server.http_date_now(),
                  "Allow": "GET, POST",
                  "Charset": "UTF-8"}
        
        code = "200 OK"
        
        streamout = b""
        fsize = 0
        
        if len(f) > 0:
            
            if f[-1] == r'/': f += 'index.py'
            
            if content['method'] == 'POST':
                post = misc.compile_keys_values(content['content'].decode())
            else:
                post = dict()
                    
            if 'Charset' in content['header'].keys():
                charset = content['header']['Charset']
            else:
                charset = 'UTF-8'
                        
            f = f.replace(r'/', SEPARATOR)
            cfile = File(self.__inidir + f)
                      
            if  cfile.get_ext() is None:
                f = cfile.get_filename()
                cfile.set_filename(f + SEPARATOR + "index.py") 
            
            header["Content-Type"] = self.__content_type[cfile.get_ext()] if  cfile.get_ext() in self.__content_type.keys() else "application/octet-stream"
            #with open(r"vars.json", "w") as f:
            #    out = '{"get":%s, "post":%s}' % (json.dumps(get), json.dumps(post))
            #    f.write(out)
            #    f.close()
            
            peer = tcpconn.getpeername()
            idsess = ("%s%i%s" % (peer[0],peer[1],str(datetime.now()))).replace(".","").replace("-","").replace(" ","").replace(":","")
            s = SingleTableDB()
            
            #salvando variaveis get
            s.set_source("getvars.tab")
            #dget  = json.dumps(get)
            for k in get.keys():
                s.insert({"idSession":idsess,"key":k,"value":get[k]})
            
            #salvando variaveis post
            s.set_source("postvars.tab")
            #dpost = json.dumps(post)
            for k in post.keys():
                s.insert({"idSession":idsess,"key":k,"value":post[k]})
            
            try:
                with open(cfile.get_filename(),'r+b') as f:
                    code = "200 OK"
                    if cfile.get_ext() == "py":
                        cmd = '{} {} "{}" charset="{}"'.format(EXEC, cfile.get_filename(), idsess, charset)
                        process = os.popen(cmd)
                        streamout = process.read().encode("UTF-8")
                        process.close()
                        header["Content-Type"] = self.__content_type["html"]                
                    else: 
                        streamout = f.read()
                    f.close()
            except Exception as ex:
                print(ex)
                header["Content-Type"] = self.__content_type["html"]
                code = "404 NOT_FOUND"
                streamout = ("""
                <html>
                    <head>
                        <meta charset="utf-8"/>
                        <title>%s</title>
                    </head>
                <body>
                    <h3>Arquivo não encontrado</h3>
                </body>
                </html>""" % self.__name).encode('UTF-8')
                
        header["Content-Length"] = str(len(streamout))
        
        #==================
        #print("from: {}\ncontent\n=======\n{}\n\nsend\n====\n{}\n(end)\n\n".format(tcpconn.getpeername(),content,header))
        
        self.send_response(tcpconn,code,header,streamout)
    
    def clear_vars(self):
        s = SingleTableDB()
        s.set_source("getvars.tab")
        s.delete("1")
        s.set_source("postvars.tab")
        s.delete("1")
#

if __name__ == "__main__":
    
    import _thread
    import sys
    
    def mainloop(server):
        print("Servidor rodando!(%s)" % SYSTEM["host"])
        server.main()
    
    try:
        server = PyServer(name=CONFIG["name"], port=int(CONFIG["port"]),inidir=CONFIG["dir"])
        server.clear_vars()
    except Exception as ex:
        print(ex)
        exit(0)
    
    _thread.start_new_thread(mainloop, (server,))
    
    while True:
        q = input()
        if q == 'q':
            break
    
    server.close()
        
    print("Servidor parado!")
    
    sys.exit(0)
    
