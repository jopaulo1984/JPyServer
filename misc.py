import urllib.parse as urlp

def compile_keys_values(content):
    result = dict()
    atributs = content.split('&')
    for a in atributs:
        kv = a.split('=')
        if len(kv) == 2:
            result[kv[0]] = urlp.unquote_plus(kv[1])
    return result

