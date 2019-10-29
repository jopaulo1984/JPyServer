import sys
import fileinfo as fi

def get_idsession():
    return sys.argv[2]

def clear_vars(self, exp="1"):
    s = SingleTableDB()
    s.set_source("getvars.tab")
    s.delete(exp)
    s.set_source("postvars.tab")
    s.delete(exp)
    s.set_source("sessvars.tab")
    s.delete(exp)

def clear_vars_session(self, sessid):
    clear_vars("id = %s" %sessid)

if __name__ == "__main__":
    from stdb.stdb import *
    cfile = fi.File(sys.argv[1])
    sys.path.append(cfile.get_dir())
    __import__(cfile.get_name().replace(".py",""))
