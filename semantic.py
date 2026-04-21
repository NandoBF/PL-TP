from symbols import SymbolTable, SemanticError

def analyze_semantics(ast):
    table = SymbolTable()


    def traverse(node):
        if node is None:
            return

        if isinstance(node, list):
            for instruction in node:
                traverse(instruction)
            return
        
        node_type = node[0]

        if node_type == 'program':
            program_name = node[1]
            instructions = node[2]
            print(f"Initializing semantic analysis for program: {program_name}")
            traverse(instructions)

        elif node_type == 'declare':
            data_type = node[1]
            variable_list = node[2]

            for var in variable_list:
                nat = var[0]
                name = var[1]
                try:
                    if nat == 'array':
                        size = var[2]
                        table.declare(name, data_type, is_array=True, size=size)
                    else:
                        table.declare(name, data_type)
                except SemanticError as e:
                    print(e)

        elif node_type == 'assign':
            target = node[1]
            target_name = target[1]
            expression = node[2]
            try:
                info = table.lookup(target_name)
                
                # needs to validate here i think

                table.initialize(target_name)
            except SemanticError as e:
                print(e)

    traverse(ast)
    print("\n--- Final symbol table ---\n")
    # import pprint
    # pprint.pprint(table.__table)
        
