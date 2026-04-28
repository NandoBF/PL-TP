import ply.yacc as yacc

class SemanticError(Exception):
    pass

class SymbolTable():
    def __init__(self):
        self.__scopes = [{}]


    def enter_scope(self):
        self.__scopes.append({})

    def exit_scope(self):
        if len(self.__scopes) > 1:
            self.__scopes.pop()




    # searches for a variable and return info on it
    def lookup(self, id):
        for scope in reversed(self.__scopes):
            if id in scope:
                return scope[id]
        raise SemanticError(f"Semantic Error: Variable or function '{id}' not declared!")


    def declare(self, id, data_type, is_array=False, size=None):
        curr_scope = self.__scopes[-1]
        if id in curr_scope:
            raise SemanticError(f"Semantic Error: Double Declaration: '{id}' already exists in this scope!")

        curr_scope[id] = {
            'nature': 'variable',
            'type': data_type,
            'is_array': is_array,
            'size': size,
            'initialized': False
        }

    def initialize(self, id):
        for scope in reversed(self.__scopes):
            if id in scope:
                scope[id]['initialized'] = True
                return

        raise SemanticError(f"Semantic Error: Variable not declared: '{id}' when trying to initialize.")


    def declare_function(self, id, return_type, arg_num):
        global_scope = self.__scopes[0]
        if id in global_scope:
            raise SemanticError(f"Semantic Error: Function or variable '{id}' already exists globally!")
    
        global_scope[id] = {
            'nature': 'function',
            'type': return_type,
            'arg_num': arg_num,
            'initialized': True
        }


    def __str__(self):
        return str(self.__scopes)
        
