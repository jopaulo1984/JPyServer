#!/usr/bin/python3

r"""Compilador da linguagem JP

Sobre:
  - Autor: João Paulo
  - Versão: 1.0 - Testes
  - Homepage: http://jpcompweb.com.br
"""

import os
from os import path

class TokenTypes:
    KEY = 0
    ID = 1
    ADDRESS = 2
    FLOAT = 6
    CHAR = 7
    STRING = 8
    HEX = 9
    INT = 10
    ESPCAR = 11
    DATE = 12
    DATETIME = 13
    ARRAY = 14
    BOOL = 15

class ControlChars:
    NL = 13
    EOT = 0x04


class Token:
    TYPES = {
        TokenTypes.KEY:"KEY",
        TokenTypes.ID:"ID",
        TokenTypes.ADDRESS:"ADDRESS",
        TokenTypes.FLOAT:"FLOAT",
        TokenTypes.CHAR:"CHAR",
        TokenTypes.STRING:"STRING",
        TokenTypes.HEX:"HEX",
        TokenTypes.INT:"INT",
        TokenTypes.ESPCAR:"ESPCAR",
        TokenTypes.BOOL:"BOOL"
    }
    def __init__(self, value, ttype, line, column):
        self.type = ttype
        self.value = value
        self.line = line
        self.column = column

    def tuple(self):
        return self.value, self.type, self.line
    
    def __str__(self):
        return "<type=%s, value='%s'>" % (Token.TYPES[self.type], self.value)
#
class TokenList:
    def __init__(self):
        self.tokens = []
        self.index = 0

    def __getitem__(self, index):
        return self.tokens[index]

    def __len__(self):
        return len(self.tokens)

    def append(self, token):
        if token:
            self.tokens.append(token)

    def read(self):
        if self.index < 0:
            self.index = -1
            return
        elif self.index < len(self.tokens):
            return self.tokens[self.index]
        else:
            self.index = len(self.tokens)

    def next(self):
        self.index += 1
        return self.read()

    def previus(self):
        self.index -= 1
        return self.read()

    def clear(self):
        self.tokens.clear() # = []

    def items(self):
        return self.tokens

    def reset(self):
        self.index = -1
#
class AnLexical:
    def __init__(self):
        self.__tokens = TokenList()
        self.__erros = []
        
    def get_tokens(self, code, retempty=False):
        
        texto = code
        
        def _next_(pos):
            if pos < len(texto):
                return texto[pos], pos + 1
            return None, pos + 1

        def _letra_(car):
            return (car != None) and (('a'<=car and car<='z') or ('A'<=car and car<='Z') or (car=='_'))

        def _num_(car):
            return (car != None) and (('0'<=car and car<='9'))

        def _hex_(car):
            return (car != None) and (_num_(car) or ('a'<=car and car<='f') or ('A'<=car and car<='F'))

        self.__tokens.clear() # = TokenList()
        pos = 0
        row = 0
        col = 0
        column = 0
        estado = 0
        temp = ''
        msg = ''

        while (estado > -1) and (estado < 255):
            if estado == 0:
                car, pos = _next_(pos)
                if not car:
                    estado = 255
                elif (car == ' ' or car == '\t') and not retempty:
                    pass
                elif _letra_(car):
                    estado = 1
                    column = col
                    temp = car
                elif car == '0':
                    estado = 2
                    column = col
                    temp = car
                elif _num_(car):
                    estado = 4
                    column = col
                    temp = car
                elif car == "'":
                    estado = 10
                elif car == '"':
                    estado = 12
                elif car in ('<','>'):
                    estado = 13
                    column = col
                    temp = car
                elif car == '[':
                    estado = 14
                    column = col
                    temp = car
                elif car == '#':
                    estado = 15
                    column = col
                    temp = ''
                else:
                    if car == '\n':
                        if retempty:
                            self.__tokens.append(Token(car, TokenTypes.ESPCAR, row, col))
                        row += 1
                        col = -1
                    else:
                        self.__tokens.append(Token(car, TokenTypes.ESPCAR, row, col))
                    temp = ''

            elif estado == 1:
                car, pos = _next_(pos)
                if _letra_(car) or _num_(car):
                    temp += car
                else:
                    if temp.lower() in ('true','false'):
                        self.__tokens.append(Token(temp , TokenTypes.BOOL, row, column))
                    else:
                        self.__tokens.append(Token(temp , TokenTypes.ID, row, column))
                    temp = ''
                    estado = 0
                    pos -= 1
            elif estado == 2:
                car, pos = _next_(pos)
                if car == 'x' or car == 'X':
                    estado = 3
                    temp += car
                elif _num_(car):
                    estado = 4
                    temp += car
                elif _letra_(car):
                    msg = "Erro de sintaxe: identificador '{}' inválido".format(car)
                    estado = -1
                else:
                    estado = 0
                    self.__tokens.append(Token(temp, TokenTypes.INT, row, col))
                    temp = ''
                    pos -= 1
            elif estado == 3:
                car, pos = _next_(pos)
                if _hex_(car):
                    temp += car
                elif _letra_(car):
                    temp += car
                    msg = "Erro de sintaxe: identificador '{}' inválido".formatToken(temp)
                    estado = -1
                elif not temp  in  ['0x','0X']:
                    self.__tokens.append(Token(temp, TokenTypes.HEX, row, col))
                    estado = 0
                    temp = ''
                    pos -= 1
                else:
                    msg = "Erro de sintaxe: identificador '{}' inválido".formatToken(temp)
                    estado = -1

            elif estado == 4:
                car, pos = _next_(pos)
                if _num_(car):
                    temp += car
                elif car == '.':
                    temp += car
                    estado = 5
                elif _letra_(car):
                    temp += car
                    msg = "Erro de sintaxe: identificador '{}' inválido".format(temp)
                    estado = -1
                else:
                    self.__tokens.append(Token(temp, TokenTypes.INT, row, col))
                    estado = 0
                    temp = ''
                    pos -= 1
            elif estado == 5:
                car, pos = _next_(pos)
                if _num_(car):
                    temp += car
                elif _letra_(car):
                    temp += car
                    msg = "Erro de sintaxe: identificador '{}' inválido".format(temp)
                    estado = -1
                else:
                    self.__tokens.append(Token(temp, TokenTypes.FLOAT, row, col))
                    estado = 0
                    temp = ''
                    pos -= 1
            elif estado == 10:
                car, pos = _next_(pos)
                if not car:
                    msg = "Erro de sintaxe: Esperado o caracter '."
                    estado = -1
                elif car == "'":
                    if len(temp) > 1:
                        self.__tokens.append(Token(temp, TokenTypes.STRING, row, column))
                    else:
                        self.__tokens.append(Token(temp, TokenTypes.CHAR, row, column))
                    estado = 0
                    temp = ''
                else:
                    temp += car
            elif estado == 12:
                car, pos = _next_(pos)
                if not car:
                    msg = 'Erro de sintaxe: Esperado o caracter ".'
                    estado = -1
                elif car == '"':
                    self.__tokens.append(Token(temp, TokenTypes.STRING, row, col))
                    estado = 0
                    temp = ''
                else:
                    temp += car
                    
            elif estado == 13:
                car, pos = _next_(pos)
                tk = temp
                if not car:
                    estado = 0
                elif car in ('>','=','<'):
                    tk = temp + car
                    estado = 0
                    temp = ''
                else:
                    pos -= 1
                    estado = 0
                self.__tokens.append(Token(tk, TokenTypes.ESPCAR, row, column))
            elif estado == 14:
                car, pos = _next_(pos)
                if not car:
                    msg = 'Erro de sintaxe: Esperado o caracter ".'
                    estado = -1
                elif car == ']':
                    self.__tokens.append(Token(temp + car, TokenTypes.ARRAY, row, col))
                    estado = 0
                    temp = ''
                else:
                    temp += car
            elif estado == 15:
                car, pos = _next_(pos)
                if not car:
                    msg = 'Erro de sintaxe: Esperado o caracter ".'
                    estado = -1
                elif car == '#':
                    self.__tokens.append(Token(temp, TokenTypes.DATE, row, col))
                    estado = 0
                    temp = ''
                elif car == ' ':
                    estado = 16
                    temp += car
                else:
                    temp += car
                    
            elif estado == 16:
                car, pos = _next_(pos)
                if not car:
                    msg = 'Erro de sintaxe: Esperado o caracter ".'
                    estado = -1
                elif car == '#':
                    self.__tokens.append(Token(temp, TokenTypes.DATETIME, row, col))
                    estado = 0
                    temp = ''
                else:
                    temp += car                
                    
            col+=1


            if estado < 0:
                self.__erros.append((row+1, col+1, msg))
        
        return self.__tokens
        
    def get_errors(self):
        return self.__erros
    
    def get_tokenslist(self):
        return self.__tokens
        
    def set_filename(self, value):
        if value is not None and not path.isfile(value):
            raise Exception("O arquivo '{}' não foi encontrado.".format(value))
        self.__fname = value
        
    def has_error(self):
        return len(self.__erros) > 0
#
