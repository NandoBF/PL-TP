def optimize_ast(ast):
    if ast is None:
        return None
    
    if isinstance(ast, list):
        return [optimize_ast(node) for node in ast]
        
    if not isinstance(ast, tuple) or len(ast) == 0:
        return ast

    node_type = ast[0]
    
    if node_type == 'program':
        return ('program', ast[1], optimize_ast(ast[2]))
        
    elif node_type == 'labeled':
        return ('labeled', ast[1], optimize_ast(ast[2]))
        
    elif node_type == 'function_def':
        return ('function_def', ast[1], ast[2], ast[3], optimize_ast(ast[4]))
        
    elif node_type == 'assign':
        return ('assign', ast[1], optimize_ast(ast[2]))
        
    elif node_type == 'binop':
        op = ast[1]
        left = optimize_ast(ast[2])
        right = optimize_ast(ast[3])
        
        # Otimização: Constant Folding (Dobragem de Constantes)
        if left[0] == 'num' and right[0] == 'num':
            if op == '+': return ('num', left[1] + right[1])
            elif op == '-': return ('num', left[1] - right[1])
            elif op == '*': return ('num', left[1] * right[1])
            elif op == '/': 
                if right[1] != 0:
                    return ('num', int(left[1] / right[1]))
                    
        return ('binop', op, left, right)
        
    elif node_type == 'relop':
        op = ast[1]
        left = optimize_ast(ast[2])
        right = optimize_ast(ast[3])
        
        # Otimização: Constant Folding em Expressões Relacionais
        if left[0] == 'num' and right[0] == 'num':
            if op == '.EQ.': return ('bool', left[1] == right[1])
            elif op == '.NE.': return ('bool', left[1] != right[1])
            elif op == '.GT.': return ('bool', left[1] > right[1])
            elif op == '.LT.': return ('bool', left[1] < right[1])
            elif op == '.GE.': return ('bool', left[1] >= right[1])
            elif op == '.LE.': return ('bool', left[1] <= right[1])
            
        return ('relop', op, left, right)
        
    elif node_type == 'not':
        expr = optimize_ast(ast[1])
        if expr[0] == 'bool':
            return ('bool', not expr[1])
        return ('not', expr)
        
    elif node_type == 'logop':
        op = ast[1]
        left = optimize_ast(ast[2])
        right = optimize_ast(ast[3])
        
        # Otimização: Constant Folding Lógico
        if left[0] == 'bool' and right[0] == 'bool':
            if op == '.AND.': return ('bool', left[1] and right[1])
            elif op == '.OR.': return ('bool', left[1] or right[1])
            
        # Otimização: Short-circuit (Dead Code Elimination)
        if left[0] == 'bool':
            if op == '.AND.' and left[1] == False:
                return ('bool', False)
            if op == '.OR.' and left[1] == True:
                return ('bool', True)
                
        return ('logop', op, left, right)
        
    elif node_type == 'if':
        cond = optimize_ast(ast[1])
        then_branch = optimize_ast(ast[2])
        else_branch = optimize_ast(ast[3]) if ast[3] is not None else None
        
        # Otimização: Eliminação de Código Morto em IFs (Dead Code Elimination)
        if cond[0] == 'bool':
            if cond[1] == True:
                return ('block', then_branch) # Vai executar sempre
            else:
                if else_branch is not None:
                    return ('block', else_branch) # Vai executar o else sempre
                else:
                    return ('nop',) # Ignora o if por completo (condição falsa)
                    
        return ('if', cond, then_branch, else_branch)
        
    elif node_type == 'print':
        return ('print', [optimize_ast(expr) for expr in ast[1]])
        
    elif node_type == 'function_call':
        return ('function_call', ast[1], [optimize_ast(arg) for arg in ast[2]])
        
    elif node_type == 'array_ref':
        return ('array_ref', ast[1], optimize_ast(ast[2]))
        
    elif node_type == 'do':
        return ('do', ast[1], ast[2], optimize_ast(ast[3]), optimize_ast(ast[4]))
        
    return ast
