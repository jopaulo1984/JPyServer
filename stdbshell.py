
def get_help():
    return """
stdbshell.py
Author: João Paulo F. Silva

comando: stdbshell.py [opções]

Opções:
  -f : abre um arquivo com os dados da tabela.
  -s : lê os comandos a partir de um arquivo.
  -h : mostra esta tela.
"""

if __name__ == "__main__":
    
    import sys
    import stdb.stdb as st
    
    s = st.SingleTableDB()
    if len(sys.argv) > 1:
        if sys.argv[1] in ('-f','-s'):
            if len(sys.argv) > 2:
                if sys.argv[1] == '-f':
                    s.set_source(sys.argv[2])
                else:
                    try:
                        with open(sys.argv[2], 'r') as f:
                            for q in s.split_query(f.read()):
                                try:
                                    s.query(q, verbose=True)
                                except Exception as ex:
                                    print(get_help())
                            f.close()
                    except: 
                        print(get_help())
                    exit(0)
            else:
                print(get_help())
                exit(0)
        elif sys.argv[1] == '-h':
            print(get_help())
            exit(0)
                
    
    print(st.get_info())
    
    acc = ""
    
    l = 1
    while True:
        
        line = input("{:<3}> ".format(l)).strip()
        
        if line =="exit" and acc == "": break
        
        if len(line) == 0 or line[-1] == ';':
            for q in s.split_query(acc + line):
                try:
                    s.query(q, verbose=True)
                except Exception as ex:
                    print(ex)
            acc = ""
            print("(end)")
            l = 1
        else:
            acc += line + "\n"
            l += 1
    
    exit(0)
    
    
