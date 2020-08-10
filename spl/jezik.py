import sly
import sys
import random

# pylint: disable=undefined-variable,function-redefined,unused-variable

#####################
# RESERVED WORDS
#####################

t_reserved = {
    'niska': 'STR',
    'niz': 'STR',
    'broj': 'INT',
    'funkcija': 'FUNC',
    'vrati': 'RETURN',
    'ako': 'IF',
    'dok': 'WHILE',
    'inace': 'ELSE',
    'ili': 'OR',
    'and': 'AND',
    'promenljiva': 'VAR',
    'true': 'TRUE',
    'false': 'FALSE',
    'null': 'NULL',
    'bool': 'BOOL'
}

#############################
# LANGUAGE TYPES TO PY TYPES
#############################

type_dict = {
    'niska': str,
    'niz': str,
    'broj': float,
    'bool': bool,
    'promenljiva': object
}

########################
# BUILT IN FUNCTION DICT
########################

built_in_functions = {}

######################
# LEXER
######################

class Lexer(sly.Lexer):

    tokens = list(t_reserved.values()) + [
        "ID", "NUMBER", "STRING", "NL", "ASSIGN",
        "PLUS", "MINUS", "MUL", "DIV", "COMPSYMB"
    ]

    ignore = " \t\n"
    literals = { '(', ')', '{', '}', "," }

    @_(r'\/\/.*')
    def comment(self, t):
        self.index += 1

    @_(r'\"(?:\\.|[^\\])*?\"')
    def STRING(self, t):
        t.value = t.value[1:-1].replace("\\\"", "\"")
        return t

    @_(r'[a-zA-Z_\$][a-zA-Z0-9_\.]*')
    def ID(self, t):
        if t.value in t_reserved:
            t.type = t_reserved[t.value]
        return t

    @_(r'\d*\.\d+|\d+')
    def NUMBER(self, t):
        t.value = type_dict['broj'](t.value)
        return t

    @_(r';+')
    def NL(self, t):
        self.lineno += t.value.count('\n')
        return t

    COMPSYMB = r"==|!=|<=|<|>=|>"
    ASSIGN = r'='
    PLUS = r'\+'
    MINUS = r'-'
    DIV = r'\/'
    MUL = r'\*'

    def error(self, t):
        raise LexerError(f"Ne poznati karakter blizu linije {self.lineno}: '{t.value[0]}'")

######################
# PARSER
######################

class Parser(sly.Parser):
    tokens = Lexer.tokens

    precedence = (
        ('left', 'AND', 'OR'),
        ('left', 'COMPSYMB'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MUL', 'DIV'),
        ('right', 'UMINUS')
    )

    @_('statements statement')
    def statements(self, p):
        return p.statements + [p.statement]

    @_('statement')
    def statements(self, p):
        return [p.statement]

    ## STATEMENTS
    
    @_('expr NL')
    def statement(self, p):
        return p.expr
    
    @_('vtype ID [ ASSIGN expr ] NL')
    def statement(self, p):
        local = False
        name = p.ID
        if p.ID[0] == "$":
            local = True
            name = p.ID[1:]
        
        if p.expr is None:
            return ("assign_type", "=", local, name, p.vtype, ('value', type_dict[p.vtype]()))
        return ("assign_type", p.ASSIGN, local, name, p.vtype, p.expr)

    @_('IF expr "{" statements "}" [ ELSE "{" statements "}" ]')
    def statement(self, p):
        return ('ifstmt', p.expr, p.statements0, p.statements1)

    @_('WHILE expr "{" statements "}"')
    def statement(self, p):
        return ('while_loop', p.expr, p.statements)

    @_('FUNC ID "(" [ idlist ] ")" "{" statements "}"')
    def statement(self, p):
        args = p.idlist
        if args is None:
            args = []
        return ('func_def', p.ID, args, p.statements)

    @_('RETURN [ expr ] NL')
    def statement(self, p):
        expr = p.expr
        if expr is None:
            expr = ('str', 'null')
        return ('return', expr)

    ## LISTS

    @_("vtype ID { ',' vtype ID }")
    def idlist(self, p):
        types = [p.vtype0, *p.vtype1]
        names = [p.ID0, *p.ID1]
        return dict(zip(names, types))

    @_('STR',
       'INT',
       'VAR',
       'BOOL')
    def vtype(self, p):
        return p[0]

    @_("expr { ',' expr }")
    def arglist(self, p):
        return [p.expr0, *p.expr1]

    ## EXPR

    @_('expr PLUS expr')
    def expr(self, p):
        return ("add", p.expr0, p.expr1)

    @_('expr MINUS expr')
    def expr(self, p):
        return ("sub", p.expr0, p.expr1)

    @_('expr MUL expr')
    def expr(self, p):
        return ("mul", p.expr0, p.expr1)

    @_('expr DIV expr')
    def expr(self, p):
        return ("div", p.expr0, p.expr1)

    @_('expr COMPSYMB expr')
    def expr(self, p):
        return ("cond", p[1], p.expr0, p.expr1)

    @_('expr AND expr')
    def expr(self, p):
        return ("and", p.expr0, p.expr1)

    @_('expr OR expr')
    def expr(self, p):
        return ("or", p.expr0, p.expr1)

    @_('MINUS expr %prec UMINUS')
    def expr(self, p):
         return ('negate', p.expr)

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr

    @_('ID "(" [ arglist ] ")"')
    def expr(self, p):
        local = False
        args = p.arglist
        if args is None:
            args = []
        if p.ID[0] == "$":
            local = True
            p.ID = p.ID[1:]
        return ('func_call', local, p.ID, args)

    @_('ID')
    def expr(self, p):
        if p.ID[0] == "$":
            return ('id_local', p.ID[1:])
        return ('id', p.ID)

    @_('NUMBER')
    def expr(self, p):
        return ('num', p.NUMBER)

    @_('STRING')
    def expr(self, p):
        return ('str', p.STRING)

    @_('TRUE')
    def expr(self, p):
        return ('value', True)

    @_('FALSE')
    def expr(self, p):
        return ('value', False)

    @_('NULL')
    def expr(self, p):
        return ('value', NullValue())

    def error(self, p):
        if p:
            raise SyntaxError(f"Sintaksna greska blizu '{p.value}' na liniji {p.lineno}")
        else:
            raise SyntaxError("Sintaksna greska na kraju fajla")

######################
# VALUE CLASSES
######################

class BaseFunction:
    def __init__(self, name, tree, arg_names=[]):
        self.name = name
        self.tree = tree
        self.arg_names = arg_names

    def __repr__(self):
        return f"<function '{self.name}'>"

    def run(self, *args):
        itp = Interpreter()

        localvars = {}

        # Setup args
        for i, arg in enumerate(args):
            if i < len(self.arg_names):
                localvars[self.arg_names[i]] = arg
            else:
                localvars["arg"+str(i)] = arg

        return itp.run(self.tree, localvars)

class NullValue:
    def __repr__(self):
        return '<null>'

class NoReturnValue:
    def __repr__(self):
        return '<no-ret>'

######################
# ERROR CLASSES
######################
class LexerError(Exception):
    """Raised when an error occures in the lexing process"""
    pass

class SyntaxError(Exception):
    """Raised when an error occures in the parsing process"""
    pass

class InterpreterError(Exception):
    """Raised when an error occures during code execution"""
    pass

######################
# INTERPRETER
######################

class Interpreter:
    def __init__(self):
        self.variables = {}

    # Top tree level evaluator (main, functions, if statements)
    def run(self, tree, localvars={}, default_ret_val=None):
        'Executes a tree parsed by a parser'
        return_value = default_ret_val

        for node in tree:
            if node[0] == "return":
                return_value = self.eval_node(node[1], localvars=localvars)
                break
            else:
                if node[0] == "func_call":
                    self.eval_node(node, localvars=localvars)
                else:
                    cret = self.eval_node(node, localvars=localvars)
                    if cret is not None:
                        return_value = cret
                        break

        return return_value

    def eval_node(self, node, localvars={}):
        if node[0] == 'str' or node[0] == 'value':
            return node[1]
        
        elif node[0] == 'num':
            return type_dict['broj'](node[1])

        elif node[0] == "id":
            return self.variables.get(node[1], NullValue())

        elif node[0] == "id_local":
            return localvars.get(node[1], NullValue())

        elif node[0] == "add":
            return self.eval_node(node[1], localvars=localvars) + self.eval_node(node[2], localvars=localvars)

        elif node[0] == "sub":
            return self.eval_node(node[1], localvars=localvars) - self.eval_node(node[2], localvars=localvars)

        elif node[0] == "mul":
            return self.eval_node(node[1], localvars=localvars) * self.eval_node(node[2], localvars=localvars)

        elif node[0] == "div":
            return self.eval_node(node[1], localvars=localvars) / self.eval_node(node[2], localvars=localvars)

        elif node[0] == "and":
            return True if self.eval_node(node[1], localvars=localvars) and self.eval_node(node[2], localvars=localvars) else False

        elif node[0] == "or":
            return True if self.eval_node(node[1], localvars=localvars) or self.eval_node(node[2], localvars=localvars) else False

        elif node[0] == "assign_type":
            local = node[2]
            tempdict = None
            if local:
                tempdict = localvars
            else:
                tempdict = self.variables

            vtype = node[4]
            vtype_obj = type_dict.get(vtype, str)
            value = self.eval_node(node[5], localvars=localvars)

            if vtype != "promenljiva" and not isinstance(value, vtype_obj):

                #statement_repr = f"{vtype} {node[3]} {node[1]} {value}"

                self.raise_error(f"Pokusaj dodeljivanja vrednosti koja nije '{vtype}' promenljivoj koja zahteva tu vrstu vrednosti!")

            if node[1] == "=":
                tempdict[node[3]] = value

        elif node[0] == "func_def":
            self.variables[node[1]] = BaseFunction(node[1], node[3], node[2])

        elif node[0] == "func_call":
            local = node[1]
            vname = node[2]
            tempdict = None
            if local:
                tempdict = localvars
            else:
                tempdict = self.variables

            if vname not in tempdict and vname not in built_in_functions:
                self.raise_error(f"Nedefinisana {'lokalna' if local else 'globalna'} funkcija '{vname}'")

            # parse args
            fargs = self.parse_args(node[3], localvars=localvars)

            # Check if built in
            if vname in built_in_functions:
                ret = built_in_functions[vname](*fargs)
                return NullValue() if ret is None else ret

            funcvar = tempdict[vname]
            ret = NullValue()

            if isinstance(funcvar, BaseFunction):
                localcopy = {'fargs': fargs}

                for i, farg in enumerate(fargs):
                    if i < len(funcvar.arg_names):

                        arg_name = list(funcvar.arg_names.keys())[i]
                        
                        # TYPE CHECKING
                        if funcvar.arg_names[arg_name] != "promenljiva":
                            if not isinstance(farg, type_dict[funcvar.arg_names[arg_name]]):
                                self.raise_error(f"Pogresan tip vrednosti dat za funkciju {vname}.\nData vrednost {farg}, ocekivan tip: {funcvar.arg_names[arg_name]}")

                        localcopy[arg_name] = farg
                    else:
                        localcopy["arg"+str(i)] = farg

                ret = self.run(funcvar.tree, localvars=localcopy)

            else:
                self.raise_error(f"Pokusaj da se pozove ne funkcionalna vrednost '{vname}'")

            return ret

        elif node[0] == "cond":
            val1 = self.eval_node(node[2], localvars=localvars)
            val2 = self.eval_node(node[3], localvars=localvars)

            if node[1] == "==":
                if isinstance(val1, NullValue) and isinstance(val2, NullValue):
                    return True
                elif (val1 == val2):
                    return True

            elif node[1] == "!=" and (val1 != val2):
                if (isinstance(val1, NullValue) and not isinstance(val2, NullValue)):
                    return True
                elif (val1 != val2):
                    return True

            elif node[1] == ">" and (val1 > val2):
                return True

            elif node[1] == "<" and (val1 < val2):
                return True

            elif node[1] == ">=" and (val1 >= val2):
                return True

            elif node[1] == "<=" and (val1 <= val2):
                return True

            return False

        elif node[0] == "ifstmt":
            if self.eval_node(node[1], localvars=localvars):
                return self.run(node[2], localvars=localvars)
            else:
                if node[3] is not None:
                    return self.run(node[3], localvars=localvars)

        elif node[0] == "while_loop":
            while self.eval_node(node[1], localvars=localvars):
                self.run(node[2], localvars=localvars)

    def parse_args(self, tree, localvars={}):
        return_values = []

        for node in tree:
            return_values.append(self.eval_node(node, localvars=localvars))

        return return_values

    def raise_error(self, msg):
        raise InterpreterError(msg)

######################
# BUILT-IN FUNCTIONS
######################

## Decorator for built in functions
def built_in_function(func):
    built_in_functions[func.__name__] = func
    return None

@built_in_function
def napisi(*args):
    print(*args)

@built_in_function
def unos(txt=''):
    return input(txt)

@built_in_function
def tip(val):
    for type_name, type_class in type_dict.items():
        if isinstance(val, type_class):
            return type_name
    else:
        return "unknown"

@built_in_function
def izadji(code=0):
    sys.exit(code)

@built_in_function
def pretvori(val, tip):
    if tip not in type_dict:
        return NullValue()
    
    try:
        return type_dict[tip](val)
    except ValueError:
        return NullValue()

@built_in_function
def nasumican(min, max):
    return type_dict['broj'](random.randint(min, max))
