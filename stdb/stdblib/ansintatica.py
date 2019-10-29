
from .anlexical import *

class BinTreeNode:    
    def __init__(self, index=0, content=None, left=None, right=None):
        self.index = index
        self.content = content
        self.left = left
        self.right = right
    
    def __str__(self):
        
        def __f(root, t, nm):
            if root is None: return ""
            r = (" " * (t * 2)) + nm  + " -> " + str(root.content.value) + "\n"
            r += __f(root.left , t + 1, "l")
            r += __f(root.right, t + 1, "r")
            return r
        
        return __f(self, 0, "root")
    
class ExpAnSintatico:
    def __init__(self):
        pass
    
    def get_tree(self, tokens):
        
        def _add(root, node):
            
            if root is None:               
                return node
            
            if node.index >= root.index:
                node.left = root
                return node
            
            if node.index < root.index:
                #if root.left is None:
                #    raise Exception("Expressão mal formada.")
                root.right = _add(root.right, node)
                return root
            
            if node.index == 0:
                raise Exception("Expressão mal formada.")
            
            return root
        
        def _f(tks, p=0):
            
            tree = None
            
            while True:
                
                tk = tks.read()
                
                if tk is None:
                    return tree
                
                if tk.value == '(':
                    tks.next()
                    node = _f(tks, p+1)
                    node.index = 1
                    tree = _add(tree, node)
                elif tk.value == ')':
                    if p==0:
                        raise Exception("')' inesperado.")
                    return tree
                else:
                    node = BinTreeNode(0, tk)
                    if tk.type == TokenTypes.ID:
                        if tk.value == 'or':
                            node.index = 5
                        elif tk.value == 'and':
                            node.index = 4
                        elif tk.value in ('like','in'):
                            node.index = 3
                        elif tk.value == 'not':
                            node.index = 2
                    elif tk.value in ('=','<>','<','>','<=','>='):
                        node.index = 3
                    tree = _add(tree, node)
                
                tks.next()
            
            return None
        
        return _f(tokens)
#

if __name__ == "__main__":
    
    while True:
        exp = input(">>")
        if exp == 'exit':
            break
        try:
            print(ExpAnSintatico().get_tree(AnLexical().get_tokens(exp)))
        except Exception as ex:
            print(ex)
        
    exit(0)
