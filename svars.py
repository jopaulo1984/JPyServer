import json
from stdb.stdb import *
import execute

GET = dict()
POST = dict()
SESSION = dict()
IDSESSION = execute.get_idsession()

def __f(s, f, ids):
    kvs = dict()
    s.set_source(f)
    for row in s.select([],"idSession='%s'" % ids):
        try:
            value = int(row["value"])
        except:
            try:
                value = float(row["value"])
            except:
                value = row["value"]
        kvs[row["key"]] = value
    return kvs

s = SingleTableDB()

GET  = __f(s, "getvars.tab" , IDSESSION)
POST = __f(s, "postvars.tab", IDSESSION)

