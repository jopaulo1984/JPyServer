#!/usr/bin/python3
#-*- encode: utf-8 -*-

import json
import re
import datetime
import shutil

if __name__ == "__main__":
    from stdblib.anlexical import *
    from stdblib.ansintatica import *
else:
    from .stdblib.anlexical import *
    from .stdblib.ansintatica import *

stdbhelp = """
Comandos:

insert  - Adiciona dados na tabela ativa.
          Os dados são adicionados entre vírgulas correspondendo
          as colunas da tabela ativa.
          Sintaxe:
            insert Column1=valor1,Column2=valor2,...,Columnn=valorn

select  - Obtém as linhas de acordo com expressão de consulta.
          Sintaxe:
            select colunas(opcional) if expressão
          onde:
            colunas   -> colunas a serem visualizadas. Caso seja ocultado, 
                         retornará todas as colunas na ordem padrão.
            expressão -> as linhas serão retornadas conforme a expressão
                         da consulta.

update  - Atualiza as linhas de acordo com expressão de consulta.
          Sintaxe:
            update coluna1=valor1,...,colunan=valorn if expressão
          Ex.:
            update nota=8.5, aprovado=true if id = 23

delete  - remove as linhas de acordo com expressão de consulta.
          Sintaxe:
            delete if expressão
          Ex.:
            delete if turma = 401 and nota < 7.0

new     - Cria uma nova tabela.
          Sintaxe:
            new TName {Column1:TIPO [options],...,Column1:TIPO [options]} in filename
          onde:
            filename -> nome do arquivo.
            TName    -> nome da tabela.
            Column   -> nome da coluna.
            TIPO     -> Tipo da coluna(INTEGER,STRING,FLOAT,DATE,DATETIME,BOOLEAN).
            options  -> (opcional)opções da coluna - AI(Auto Increment), UN(Unique), etc.
          Ex.:
            new Aluno {id:integer [AI,UN], nome:string, sobrenome:string, aprovado:boolean} in aluno.tab

open    - Abre uma tabela do arquivo.
          Sintaxe:
            open nome_do_arquivo

exit    - Sai da aplicação.
"""

def get_help():
    return stdbhelp

def get_info():
    return """
================== Single Table DB =====================
= Version: v1.0                                        =
= Author : João Paulo F. Silva <jpfs@jpcompweb.com.br> =
========================================================
"""

class VTypes:
    STRING = 0
    INT = 1
    FLOAT = 2
    DATE = 3
    DATETIME = 4
    BOOL = 5

def formatar(exp, valor):
    return exp.format(valor)

def date_to_str(dt):
    return '{}-{:02}-{:02} {:02}:{:02}:{:02}'.format(dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second)

def str_to_date(sdt):
    return datetime.datetime.strptime(sdt, '%Y-%m-%d').date()

def str_to_datetime(sdt):
    return datetime.datetime.strptime(sdt, '%Y-%m-%d %H:%M:%S').date()
#
class SingleTableDB:
    
    def __init__(self,source=None):
        
        #atributos
        self.__source = None
        self.__name = ""
        self.__cols = []
        
        self.set_source(source)
    
    def get_col_index(self, name):
        for i, col in enumerate(self.__cols):
            if col["name"] == name:
                return i
        return -1
    
    def load(self):
        if self.__source is None:
            return
            
        line0 = ""
        with open(self.__source,'r') as f:
            line0 = f.readline()
            f.close()
            
        table = json.loads(line0)
        
        self.__name = table["name"]
        self.__cols = table["columns"]
        for col in self.__cols:
            col["size"] = len(col["name"])
        
    def set_source(self, source):        
        if self.__source == source: return
        self.__source = source
        self.load()
        
    def get_source(self):
        return self.__source
        
    def set_name(self, value):
        if self.__name == value: return
        self.__name = value
        
    def get_name(self):
        return self.__name
    
    def get_cols(self):
        return self.__cols
    
    def __get_tree(self, exp):
        tree = ExpAnSintatico().get_tree(AnLexical().get_tokens(exp))
        #print(tree)
        return tree
    
    def __get_test_cols(self, tree):
        
        def _f(root, dcols):
            if root is None:
                pass
            elif root.index == 0:
                if root.content.type == TokenTypes.ID:
                    
                    if root.content.value.lower() in self.keywords():
                        raise Exception("'%s' é uma palavra chave. Palavras chaves não podem ser nome de tabela e/ou colunas." % root.content.value)
                    
                    if not root.content.value in dcols.keys():
                        cindex = self.get_col_index(root.content.value)
                        if cindex < 0:
                            raise Exception("A coluna '%s' não foi encontrada na tabela." % root.content.value)
                        dcols[root.content.value] = cindex #self.get_col_index(root.content.value)
            else:
                _f(root.left , dcols)
                _f(root.right, dcols)
            
            return dcols
        
        return _f(tree, {})
    
    def __get_compatible_value(self, col, svalue):
        if col["type"] == VTypes.INT:
            return int(svalue)
        if col["type"] == VTypes.FLOAT:
            return float(svalue)
        if col["type"] == VTypes.DATE:
            if svalue == '': return None
            return str_to_date(svalue)
        if col["type"] == VTypes.DATETIME:
            if svalue == '': return None
            return str_to_datetime(svalue)
        if col["type"] == VTypes.BOOL:
            return svalue.lower() == 'true'
        return svalue    
    
    def __get_result(self, tree, dcols, row):
        
        def _f(root, r):
            
            if root is None:
                return False
            
            if root.index == 0:
                if root.content.type == TokenTypes.ID:
                    if root.content.value.lower() in self.keywords():
                        raise Exception("'%s' é uma palavra chave. Palavras chaves não podem ser nome de tabela e/ou colunas." % root.content.value)
                    
                    try:
                        cindex = dcols[root.content.value]
                    except:
                        raise Exception("Não foi possível encontrar o identificador '%s'." % root.content.value)
                    return self.__get_compatible_value(self.__cols[cindex], r[cindex])
                else:
                    if root.content.type == TokenTypes.INT:
                        return int(root.content.value)
                    if root.content.type == TokenTypes.FLOAT:
                        return float(root.content.value)
                    if root.content.type == TokenTypes.DATE:
                        if root.content.value == "": return None
                        return str_to_date(root.content.value)
                    if root.content.type == TokenTypes.DATETIME:
                        if root.content.value == "": return None
                        return str_to_datetime(root.content.value)
                    if root.content.type == TokenTypes.BOOL:
                        return root.content.value.lower() == 'true'
                    return root.content.value
            
            rvalue = _f(root.left , r)
            qvalue = _f(root.right, r)
            
            oper = root.content.value
            
            if oper == 'or':
                return rvalue or qvalue
            if oper == 'and':
                return rvalue and qvalue
            if oper == '=':
                return rvalue == qvalue
            if oper == '<>':
                return rvalue != qvalue
            if oper == '<':
                return rvalue < qvalue
            if oper == '>':
                return rvalue > qvalue
            if oper == '>=':
                return rvalue >= qvalue
            if oper == '<=':
                return rvalue <= qvalue
            if oper == 'in':
                return rvalue in json.loads(qvalue)
            if oper == 'like':
                return re.search(qvalue, rvalue) is not None
            if oper == 'not':
                return not qvalue
            raise Exception("Esperado um operador, mas encontrado '%s'." % oper)
            
        
        return _f(tree, row)
    
    def __compile_kvs(self, kvs):
        result = {}
        estd = 0
        key = ""
        tks = AnLexical().get_tokens(kvs)
        while True:
            tk = tks.read()
            if estd == 0:
                if tk is None: break
                if tk.type == TokenTypes.ID:
                    key = tk.value
                    estd = 1
                else:
                    raise Exception("Esperado um identificador, mas encontrado '%s'." % tk.value)                
            elif estd == 1:
                if tk is None:
                    raise Exception("Esperado um valor para '%s'." % key)
                if tk.value == "=":
                    estd = 2
                else:
                    raise Exception("Esperado '=', mas encontrado '%s'." % tk.value)
            elif estd == 2:
                if tk is None:
                    raise Exception("Esperado um valor para '%s'." % key) 
                if tk.type == TokenTypes.INT:
                    result[key] = int(tk.value)
                elif tk.type == TokenTypes.FLOAT:
                    result[key] = float(tk.value)
                else:
                    result[key] = tk.value
                estd = 3
            elif estd == 3:
                if tk is None: break
                if tk.value == ",":
                    estd = 0
                else:
                    raise Exception("Esperado ',', mas encontrado '%s'." % tk.value)
            tks.next()
        return result
    
    def __compile_arrs(self, arrs):
        result = []
        estd = 0
        tks = AnLexical().get_tokens(arrs)
        while True:            
            tk = tks.read()
            if estd == 0:
                if tk is None: break
                if tk.type == TokenTypes.INT:
                    result.append(int(tk.value))
                elif tk.type == TokenTypes.FLOAT:
                    result.append(float(tk.value))
                else:
                    result.append(tk.value)
                estd = 1
            elif estd == 1:
                if tk is None: break
                if tk.value == ",":
                    estd = 0
                else:
                    raise Exception("Esperado ',', mas encontrado '%s'." % tk.value)
            tks.next()
        return result
    
    def __compile_cols(self, cols):
        types = {
            "STR"       :VTypes.STRING,
            "STRING"    :VTypes.STRING,
            "INT"       :VTypes.INT,
            "INTEGER"   :VTypes.INT,
            "FLOAT"     :VTypes.FLOAT,
            "DATE"      :VTypes.DATE,
            "DATETIME"  :VTypes.DATETIME,
            "BOOL"      :VTypes.BOOL,
            "BOOLEAN"   :VTypes.BOOL
        }
        result = []
        dcol = None
        estd = 0
        tks = AnLexical().get_tokens(cols)
        while True:
            tk = tks.read()
            if estd == 0:
                if tk is None: break
                if tk.type == TokenTypes.ID:
                    if tk.value.lower() in self.keywords():
                        raise Exception("'%s' é uma palavra chave. Palavras chaves não podem ser nome de tabela e/ou colunas." % tk.value)
                    dcol = {"name": tk.value}
                    estd = 1
                else:
                    raise Exception("Esperado um identificador, mas encontrado '%s'." % tk.value)
            elif estd == 1:
                if tk is None:
                    raise Exception("Erro de sintaxe. Esperado um tipo para a coluna.")
                if tk.value == ":":
                    estd = 2
                else:
                    raise Exception("Esperado ':', mas encontrado '%s'." % tk.value)
            elif estd == 2:
                if tk is None:
                    raise Exception("Erro de sintaxe. Esperado um tipo para a coluna.")
                t = tk.value.upper()
                if tk.type == TokenTypes.ID and t in types.keys():
                    dcol["type"] = types[t]
                    estd = 3
                else:
                    raise Exception("'%s' não é um tipo válido." % tk.value)
            elif estd == 3:
                if tk is None: 
                    result.append(dcol)
                    break
                if tk.type == TokenTypes.ARRAY:
                    dcol["options"] = self.__compile_arrs(re.findall(r"\[(.*)\]", tk.value)[0])
                    if "AI" in dcol["options"]:
                        if dcol["type"] != VTypes.INT:
                            raise Exception ("A opção 'AI' só poderá ser inserida nas colunas do tipo 'INTEGER'.")
                        dcol["last"] = -1
                    estd = 4
                elif tk.value == ',':
                    result.append(dcol)
                    estd = 0
                else:
                    raise Exception("Erro de sintaxe. Esperado ',', mas encontrado '%s'." % tk.value)
            elif estd == 4:
                if tk is None: 
                    result.append(dcol)
                    break
                if tk.value == ',':
                    result.append(dcol)
                    estd = 0
                else:
                    raise Exception("Erro de sintaxe. Esperado ',', mas encontrado '%s'." % tk.value)
                
            tks.next()
        return result        
    
    def __update_file(self):
        tname = self.__source + '.temp'
        with open(self.__source,'r') as f:
            with open(tname, 'w') as ft:
                ft.write(json.dumps({"name":self.__name,"columns":self.__cols}))
                f.readline()
                while True:
                    srow = f.readline()
                    if srow in ("","\n"): break
                    ft.write("\n" + srow.strip())
                ft.close()
            shutil.move(tname, self.__source)
            f.close()
    
    def __modify_rows(self, testfunc, newrowfunc, args1, args2):
        
        if not (callable(newrowfunc) and callable(testfunc)):
            return 0, 0
        
        count = 0
        modf = 0
        tname = self.__source + '.temp'
        with open(self.__source,'r') as f:
            with open(tname, 'w') as ft:
                srow = f.readline().strip()
                ft.write(srow)
                while True:
                    srow = f.readline()
                    if srow in ("","\n"): break
                    row = json.loads(srow)
                    if testfunc(row, *args1):
                        ft.write('\n' + json.dumps(newrowfunc(row, *args2)))
                        modf += 1
                    count += 1
                ft.close()
            f.close()
        shutil.move(tname, self.__source)
        return count, modf
        
    def split_query(self, q):
        arr = []
        tks = AnLexical().get_tokens(q, retempty=True)
        acc = ''
        for tk in tks.items():
            if tk.value == ';':
                arr.append(acc)
                acc = ''
            elif tk.type == TokenTypes.STRING:
                acc += "'%s'" % tk.value.replace("'",r"\u0027")
            else:
                acc += tk.value
        if acc != '': arr.append(acc)
        return arr
    
    def keywords(self):
        return ('true','false','in','like','if','order','insert','select','update','delete','new','and','or','not')
    
    #-------------------------
    def select(self, columns, exp, assoc=True):
        
        cols = []
        
        if len(columns) == 0:
            cols = [i for i in range(len(self.__cols))]
        else:
            for nm in columns:
                cindex = self.get_col_index(nm)
                if cindex < 0:
                    print("A coluna '%s' não foi encontrada na tabela." % nm)
                    return []
                cols.append(cindex)
            
        try:
            rows = []
            tree = self.__get_tree(exp)
            dcols = self.__get_test_cols(tree)
            with open(self.__source,'r') as f:
                f.readline()
                while True:
                    srow = f.readline()
                    if srow in ("","\n"): break
                    row = json.loads(srow)
                    if assoc: newrow = {}
                    else: newrow = []
                    if self.__get_result(tree, dcols, row) == True:
                        for c in cols:
                            col = self.__cols[c]
                            val = row[c]
                            if assoc: newrow[col["name"]] = val
                            else: newrow.append(val)
                            rs = len(str(val))
                            if col["size"] < rs:
                                col["size"] = rs
                        rows.append(newrow)
                f.close()
                return rows
                
        except Exception as ex:
            print("Erro: ", ex)
            
        return []
    
    def insert(self, values):
        arr = []
        _allcols = []
        updt = False
        for cname in values.keys():
            if self.get_col_index(cname) < 0:
                raise Exception("Não foi encontrada a coluna '%s'." % cname)
        for col in self.__cols:
            if col["name"] in values.keys():
                if "options" in col.keys() and "AI" in col["options"]:
                    raise Exception("Não é permitido definir valor para uma coluna marcada com 'AI'.")
                _allcols.append(values[col["name"]])
            else:
                if col["type"] == VTypes.INT:
                    if "options" in col.keys() and "AI" in col["options"]:
                        col["last"] += 1
                        _allcols.append(col["last"])
                        updt = True
                    else:
                        _allcols.append(0)
                elif  col["type"] == VTypes.FLOAT:
                    _allcols.append(0.0)
                elif  col["type"] == VTypes.DATE:
                    _allcols.append("2000-01-01")
                elif  col["type"] == VTypes.DATETIME:
                    _allcols.append("2000-01-01 00:00:00")
                elif  col["type"] == VTypes.BOOL:
                    _allcols.append(False)
                else:
                    _allcols.append("")
        if updt: self.__update_file()
        with open(self.__source, 'a') as f:
            f.write("\n" + json.dumps(_allcols))
            f.close()
        
        return _allcols
        
    def update(self, dvalues, exp):
        
        if len(dvalues.keys()) == 0: return 0
        
        def __f(row, icols, tree, dcols):
            if self.__get_result(tree, dcols, row):
                for c, val in icols:
                    row[c] = val
            return row
        
        result = 0
        
        icols = []
        for nm in dvalues.keys():
            cindex = self.get_col_index(nm)
            if cindex < 0:
                print("A coluna '%s' não foi encontrada na tabela." % nm)
                return
            icols.append((cindex, dvalues[nm]))
        
        tree = self.__get_tree(exp)
        dcols = self.__get_test_cols(tree)
        
        count, modf = self.__modify_rows(lambda row: True, __f, (), (icols,tree, dcols))
        
        return modf
        
        tname = self.__source + '.temp'
        with open(self.__source,'r') as f:
            with open(tname, 'w') as ft:
                srow = f.readline()
                ft.write(srow)
                while True:
                    srow = f.readline()
                    if srow in ("","\n"): break
                    row = json.loads(srow)
                    
                    if self.__get_result(tree, dcols, row) == True:
                        for c, val in icols:
                            row[c] = val
                        ft.write(json.dumps(row) + '\n')
                        result += 1
                    else:
                        ft.write(srow)
                    
                ft.close()
            shutil.move(tname, self.__source)
            f.close()
        
        return result
        
    def delete(self, exp):
                
        def __f(row, tree, dcols):
            if not self.__get_result(tree, dcols, row):
                return True
            return False
        
        tree = self.__get_tree(exp)
        dcols = self.__get_test_cols(tree)
        
        count, modf = self.__modify_rows(__f, lambda row: row, (tree, dcols),())
        
        #open pessoa.tab; select if 1; delete if id = 1;
        
        return count - modf
    
    def update_table(self, name, columns):
        pass
    
    def new(self, source, name, columns):
        self.__source = source
        with open(source, 'w') as f:
            header = {"name":name,"columns":columns}
            f.write(json.dumps(header))
            f.close()
        self.load()
    
    #-------------------------------
    def query(self, q, verbose=False):
        
        if q is None: return
        if len(re.findall(r'^([\n\s\t]*)$', q)) > 0: return
        
        q = q.strip()
        
        arr = re.findall(r"^select([\s\t].*)?[\s\t\n]+if[\s\t\n]([\w\W\d\n]*)([\s\t\n]+order by .*)?[\s\t\n]*$", q)
        if len(arr) > 0:
            icols = self.__compile_arrs(arr[0][0])      
            result = self.select(icols, arr[0][1])
            if verbose: self.print_select(icols, result)
            return result
        
        arr = re.findall(r"^insert[\s\t\n]([\n\w\W\d]*)$", q)
        if len(arr) > 0:
            row = self.insert(self.__compile_kvs(arr[0]))
            if verbose: print("Linha inserida.")
            return row
        
        arr = re.findall(r"^update[\s\t]+table[\s\t\n]+\{([\n\w\W\d]*)\}[\s\t\n]*$", q)
        if len(arr) > 0:
            columns = self.__compile_cols(arr[0])
            self.update_table(self.get_name(), columns)
            if verbose: print("A tabela foi alterada.")
            return
        
        arr = re.findall(r"^update[\s\t\n]([\n\w\W\d]*)[\s\t\n]if[\s\t\n]([\n\w\W\d]*)$", q)
        if len(arr) > 0:
            dvalues = self.__compile_kvs(arr[0][0])
            count = self.update(dvalues, arr[0][1])
            if verbose: print("%i Linha(s) atualizada(s)." % count)
            return
        
        arr = re.findall(r"^delete[\s\t\n]+if[\s\t\n]([\n\w\W\d]*)$", q)
        if len(arr) > 0:
            count = self.delete(arr[0])
            if verbose: print("%i Linha(s) deletadas(s)." % count)
            return
        
        arr = re.findall(r"^new (.*)[\s\t\n]*\{([\n\w\W\d]*)\}[\s\t\n]*in ([\n\w\W\d]*)$", q)
        if len(arr) > 0:
            tname = arr[0][0].strip()
            if not re.match(r"^[_A-Za-z][\w\d]*$", tname):
                raise Exception(("O nome '%s' não é permitido para uma tabela.\n" % tname) +
                                "O nome deve ser iniciado por uma letra ou '_' e não conter caracteres especiais.")
            columns = self.__compile_cols(arr[0][1])
            tfile = arr[0][2].strip()
            self.new(tfile, tname, columns)
            if verbose: print("A tabela '%s' foi criada com sucesso e salva no arquivo '%s'." % (tname, tfile))
            return
        
        arr = re.findall(r'^open[\s\t]+(.*)$', q)
        if len(arr) > 0:
            try:
                self.set_source(arr[0])
            except:
                print("Erro ao abrir o arquivo <%s>" % arr[0])
            return
        
        if verbose: print("Não foi possível processar a consulta <%s>." % q)
    #-------------------------------
        
    def print_select(self, columns, rows):
        
        stot = 0
        lcol = ""
        ncol = ""
        
        if len(columns) == 0: 
            cols = [i for i in range(len(self.__cols))]
        else:
            cols = [self.get_col_index(i) for i in columns]
        
        for cindex in cols:
            col = self.__cols[cindex]
            stot += col["size"] + 1
            lcol += " %s " % ("=" * col["size"])
            ncol += formatar(" {:<%s} " % col["size"], col["name"])
            
        lcol += "  "
        ncol += "  "
        stot -= 1
        lnm = len(self.get_name())
        sl = int((stot - lnm) / 2)
        sr = stot - sl - lnm
        
        tbord = " %s" % ("=" * (stot + len(cols) - 1))
        
        print("")
        print(formatar(" {:^%s} " % stot, self.get_name()))
        print(tbord)
        print(ncol)
        print(lcol)
        
        for row in rows:
            srow = ""
            for c in cols:
                k = None
                if type(row) is dict:
                    k = self.__cols[c]["name"]
                else:
                    k = c
                srow += formatar(" {:<%s} " % self.__cols[c]["size"], row[k])
            print(srow)
        
        print("")
        
        return None
        
    def __str__(self):
        if self.__source is None: return "None"
        return "Tabela '%s'" % self.get_name()
    #
#

if __name__ == "__main__":
    
    import sys
    
    def print_args_error():    
        print("Argumentos inválidos.")
        print("Digite 'help' para mais informações.")        
    
    print("============================================================")
    print("=                  Single Table DB                         =")
    print("============================================================")
    
    if len(sys.argv) > 1:
        st = SingleTableDB(sys.argv[1])
    else:
        st = SingleTableDB()
    
    while True:
        
        incmd = input('stdb >> ').strip()
        
        if incmd == 'exit':
            exit(0)
        
        if incmd == 'help':
            print(stdbhelp)
            continue
            
        try:
            for q in st.split_query(incmd):
                st.query(q, verbose=True)
        except Exception as ex:
            print(ex)
        
