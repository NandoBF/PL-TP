import ply.yacc as yacc

class SemanticError(Exception):
    pass

class SymbolTable():
    def __init__(self):
        self.__scopes = [{}]

        # memory counters for the stack based vm
        self.__global_offset = 0 # addresses for PUSHG/STOREG
        self.__local_offset = 0 # addresses for PUSHL/STOREL


    def enter_scope(self):
        self.__scopes.append({})
        self.__local_offset = 0

    def exit_scope(self):
        if len(self.__scopes) > 1:
            self.__scopes.pop()




    # searches for a variable and return info on it
    def lookup(self, id):
        for scope in reversed(self.__scopes):
            if id in scope:
                return scope[id]
        raise SemanticError(f"Semantic Error: Variable or function '{id}' not declared!")


    def declare(self, id, data_type, is_array=False, size:int|None = None):
        curr_scope = self.__scopes[-1]

        if id in curr_scope:
            if curr_scope[id].get('nature') == 'function':
                if curr_scope[id].get('type') != data_type:
                    raise SemanticError(f"Semantic Error: Function '{id}' declared with conflicting type '{data_type}'.")
                return
            raise SemanticError(f"Semantic Error: Double Declaration: '{id}' already exists in this scope!")

        size_in_memory = size if is_array else 1

        if size_in_memory is None:
            print("Triggered some lsp stub that I wrote, fix this (symbols.py)")
            return # annoying lsp warnings

        is_global = len(self.__scopes) == 1
        if is_global:
            address = self.__global_offset
            self.__global_offset += size_in_memory
        else:
            address = self.__local_offset
            self.__local_offset += size_in_memory

        curr_scope[id] = {
            'nature': 'variable',
            'type': data_type,
            'is_array': is_array,
            'size': size,
            'initialized': False,
            'address': address,
            'is_global': is_global
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


    def get_global_memory_size(self):
        return self.__global_offset


    def __str__(self):
        return str(self.__scopes)
        
