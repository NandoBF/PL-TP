from symbols import SymbolTable, SemanticError

def analyze_semantics(ast):
    table = SymbolTable()

    cycle_stack = []

    existing_labels = set()
    pending_gotos = set()

    # Register all functions first
    if isinstance(ast, list):
        for unit in ast:
            if unit[0] == 'function_def':
                return_type = unit[1]
                func_name = unit[2]
                args = unit[3]

                try:
                    table.declare_function(func_name, return_type, len(args))
                except SemanticError as e:
                    print(e)



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

        elif node_type == 'labeled':
            label = node[1]
            instruction = node[2]

            existing_labels.add(label)

            if instruction == 'continue' or (isinstance(instruction, tuple) and instruction[0] == 'continue'):
                try:
                    if len(cycle_stack) == 0:
                        raise SemanticError(f"Semantic Error: CONTINUE {label} has no opener DO cycle!")

                    label_expected = cycle_stack[-1]
                    if label != label_expected:
                        raise SemanticError(f"Semantic Error: CONTINUE {label} does not match the expected DO cycle: {label_expected}")

                    cycle_stack.pop()
                except SemanticError as e:
                    print(e)


            else: traverse(instruction)

        elif node_type == 'goto':
            target_label = node[1]

            pending_gotos.add(target_label)

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
                table.lookup(target_name)
                    
                traverse(expression)

                table.initialize(target_name)
            except SemanticError as e:
                print(e)

        elif node_type == 'do':
            label = node[1]
            cycle_stack.append(label)

            iterator_name = node[2]
            try:
                table.lookup(iterator_name)
                table.initialize(iterator_name)
            except SemanticError as e:
                print(e)



        elif node_type == 'function_def':
            func_name = node[2]
            args = node[3]
            body = node[4]
            print(f"Analysing function: {func_name}")

            table.enter_scope()

            traverse(body)

            table.exit_scope()
            print(f"Exiting scope for function: {func_name}")

        elif node_type == 'function_call':
            func_name = node[1]
            arguments = node[2]

            try:
                func_info = table.lookup(func_name)
                if func_info is None:
                    raise SemanticError(f"Semantic Error: '{func_name}' is not a function or variable!")

                if func_info.get('nature') != 'function':
                    raise SemanticError(f"Semantic Error: '{func_name}' is not a function!")

                expected_arg_num = func_info['arg_num']
                actual_arg_num = len(arguments)

                if actual_arg_num != expected_arg_num:
                    raise SemanticError(f"Semantic Error: '{func_name}' expects [{expected_arg_num}] arguments but got [{actual_arg_num}]!")

                for arg in arguments:
                    traverse(arg)
            except SemanticError as e:
                print(e)

    traverse(ast)
    print("\n--- Final symbol table ---\n")

    if len(cycle_stack) > 0:
        print(f"Semantic Error: DO cycles were not closed: {cycle_stack}")

    for target_label in pending_gotos:
        if target_label not in existing_labels:
            print(f"Semantic Error: GOTO points to label {target_label}, but that label is nonexistent!")
    # import pprint
    # pprint.pprint(table.__table)
        
