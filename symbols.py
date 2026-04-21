import ply.yacc as yacc

class SemanticError(Exception):
    pass

class SymbolTable():
    def __init__(self):
        self.__table = {}


    # searches for a variable and return info on it
    def lookup(self, id):
        if id not in self.__table:
            raise SemanticError(f"Semantic Error: Variable not declared: '{id}'")
        return self.__table.get(id)

    def declare(self, id, data_type, is_array=False, size=None):
        if id in self.__table:
            raise SemanticError(f"Semantic Error: Variable already declared: '{id}'")

        self.__table[id] = {
            'type': data_type,
            'is_array': is_array,
            'size': size,
            'initialized': False
        }

    def initialize(self, id):
        if id not in self.__table:
            raise SemanticError(f"Semantic Error: Variable not declared: '{id}")
        self.__table[id]['initialized'] = True


    def __str__(self):
        return str(self.__table)
        
