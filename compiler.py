from lexer import lexer
from parser import parser
from semantic import analyze_semantics
from codegen import generate_code
from optimizer import optimize_ast
from symbols import SemanticError

def compile_file(filepath, output_path=None):
    with open(filepath, 'r') as f:
        code = f.read()
    
    ast = parser.parse(code)
    if not ast:
        raise SyntaxError("Syntax error during parsing.")
        
    ast = optimize_ast(ast)
    analyze_semantics(ast)
    vm_code = generate_code(ast)
    
    if output_path:
        with open(output_path, 'w') as f:
            f.write(vm_code)
            
    return vm_code
