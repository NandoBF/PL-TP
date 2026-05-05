from symbols import SymbolTable, SemanticError

class SemanticAnalyzer:
    def __init__(self):
        self.table = SymbolTable()
        self.cycle_stack = []
        self.existing_labels = set()
        self.pending_gotos = set()
        self.errors = []

    def analyze(self, ast):
        # Register intrinsic functions
        try:
            self.table.declare_function('MOD', 'INTEGER', 2)
        except SemanticError:
            pass

        # Register all functions first
        if isinstance(ast, list):
            for unit in ast:
                if unit[0] == 'function_def':
                    return_type = unit[1]
                    func_name = unit[2]
                    args = unit[3]
                    if '_' in func_name:
                        self.errors.append(f"Semantic Error: Identifier '{func_name}' contains an underscore, which is not supported!")
                    try:
                        self.table.declare_function(func_name, return_type, len(args))
                    except SemanticError as e:
                        self.errors.append(str(e))
        
                elif unit[0] == 'subroutine_def':
                    func_name = unit[1]
                    args = unit[2]
                    if '_' in func_name:
                        self.errors.append(f"Semantic Error: Identifier '{func_name}' contains an underscore, which is not supported!")
                    try:
                        self.table.declare_function(func_name, 'VOID', len(args))
                    except SemanticError as e:
                        self.errors.append(str(e))
        
        self.traverse(ast)
        print("\n--- Final symbol table ---\n")

        if len(self.cycle_stack) > 0:
            self.errors.append(f"Semantic Error: DO cycles were not closed: {self.cycle_stack}")

        for target_label in self.pending_gotos:
            if target_label not in self.existing_labels:
                self.errors.append(f"Semantic Error: GOTO points to label {target_label}, but that label is nonexistent!")
                
        if len(self.errors) > 0:
            error_msg = "\n".join(self.errors)
            raise SemanticError(f"Compilation failed with {len(self.errors)} semantic error(s):\n{error_msg}")

    def traverse(self, node):
        if node is None:
            return None

        if isinstance(node, list):
            for instruction in node:
                self.traverse(instruction)
            return None
        
        if not isinstance(node, tuple) or len(node) == 0:
            return None

        node_type = node[0]
        method_name = f'visit_{node_type}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        # Some nodes like 'nop' or 'return' might fall here, ignoring safely.
        pass 
        return None

    def visit_program(self, node):
        program_name = node[1]
        instructions = node[2]
        print(f"Initializing semantic analysis for program: {program_name}")
        self.traverse(instructions)

    def visit_labeled(self, node):
        label = node[1]
        instruction = node[2]

        self.existing_labels.add(label)

        if instruction == 'continue' or (isinstance(instruction, tuple) and instruction[0] == 'continue'):
            try:
                if len(self.cycle_stack) == 0:
                    raise SemanticError(f"Semantic Error: CONTINUE {label} has no opener DO cycle!")

                label_expected = self.cycle_stack[-1]
                if label != label_expected:
                    raise SemanticError(f"Semantic Error: CONTINUE {label} does not match the expected DO cycle: {label_expected}")

                self.cycle_stack.pop()
            except SemanticError as e:
                self.errors.append(str(e))
        else: 
            self.traverse(instruction)

    def visit_block(self, node):
        self.traverse(node[1])

    def visit_goto(self, node):
        target_label = node[1]
        self.pending_gotos.add(target_label)

    def visit_declare(self, node):
        data_type = node[1]
        variable_list = node[2]

        for var in variable_list:
            nat = var[0]
            name = var[1]
            if '_' in name:
                self.errors.append(f"Semantic Error: Identifier '{name}' contains an underscore, which is not supported!")
            try:
                if nat == 'array':
                    size = var[2]
                    self.table.declare(name, data_type, is_array=True, size=size)
                else:
                    self.table.declare(name, data_type)
            except SemanticError as e:
                self.errors.append(str(e))

    def visit_assign(self, node):
        target_name = node[1][1]
        expression = node[2]
        try:
            target_info = self.table.lookup(target_name)
            expr_type = self.traverse(expression)
            target_type = target_info['type']
            
            # TYPE CHECKING NA ATRIBUIÇÃO
            if expr_type is not None and expr_type != 'UNKNOWN':
                if target_type == 'LOGICAL' and expr_type != 'LOGICAL':
                    raise SemanticError(f"Semantic Error: Cannot assign {expr_type} to LOGICAL variable '{target_name}'")
                if expr_type == 'LOGICAL' and target_type != 'LOGICAL':
                    raise SemanticError(f"Semantic Error: Cannot assign LOGICAL to {target_type} variable '{target_name}'")
                if target_type == 'STRING' and expr_type != 'STRING':
                    raise SemanticError(f"Semantic Error: Cannot assign {expr_type} to STRING variable '{target_name}'")

            self.table.initialize(target_name)
        except SemanticError as e:
            self.errors.append(str(e))

    def visit_do(self, node):
        label = node[1]
        self.cycle_stack.append(label)

        iterator_name = node[2]
        try:
            self.table.lookup(iterator_name)
            self.table.initialize(iterator_name)
            self.traverse(node[3])
            self.traverse(node[4])
        except SemanticError as e:
            self.errors.append(str(e))

    def visit_function_def(self, node):
        func_name = node[2]
        body = node[4]
        print(f"Analysing function: {func_name}")

        self.table.enter_scope()
        self.traverse(body)
        self.table.exit_scope()
        print(f"Exiting scope for function: {func_name}")
        
    def visit_subroutine_def(self, node):
        func_name = node[1]
        body = node[3]
        print(f"Analysing subroutine: {func_name}")

        self.table.enter_scope()
        self.traverse(body)
        self.table.exit_scope()
        print(f"Exiting scope for subroutine: {func_name}")

    def visit_call(self, node):
        func_name = node[1]
        arguments = node[2]

        try:
            func_info = self.table.lookup(func_name)
            if func_info is None or func_info.get('nature') != 'function':
                raise SemanticError(f"Semantic Error: '{func_name}' is not a subroutine!")

            expected_arg_num = func_info['arg_num']
            actual_arg_num = len(arguments)

            if actual_arg_num != expected_arg_num:
                raise SemanticError(f"Semantic Error: '{func_name}' expects [{expected_arg_num}] arguments but got [{actual_arg_num}]!")

            for arg in arguments:
                self.traverse(arg)
        except SemanticError as e:
            self.errors.append(str(e))
        
    def visit_if(self, node):
        cond_type = self.traverse(node[1])
        if cond_type != 'LOGICAL' and cond_type != 'UNKNOWN':
            print(f"Semantic Error: IF condition must be LOGICAL, got {cond_type}")
        self.traverse(node[2])
        if node[3] is not None:
            self.traverse(node[3])
            
    def visit_print(self, node):
        for expr in node[1]:
            self.traverse(expr)
            
    def visit_read(self, node):
        for target in node[1]:
            try:
                self.table.initialize(target[1])
            except SemanticError as e:
                self.errors.append(str(e))

    def visit_num(self, node):
        return 'INTEGER'
        
    def visit_float(self, node):
        return 'REAL'
        
    def visit_bool(self, node):
        return 'LOGICAL'
        
    def visit_string(self, node):
        return 'STRING'
        
    def visit_var_ref(self, node):
        name = node[1]
        try:
            info = self.table.lookup(name)
            if not info.get('initialized', False) and info.get('nature') != 'function':
                print(f"Semantic Warning: Variable '{name}' might be uninitialized when used.")
            return info['type']
        except SemanticError as e:
            self.errors.append(str(e))
            return 'UNKNOWN'
            
    def visit_array_ref(self, node):
        name = node[1]
        try:
            info = self.table.lookup(name)
            return info['type']
        except SemanticError as e:
            self.errors.append(str(e))
            return 'UNKNOWN'
            
    def visit_binop(self, node):
        left_type = self.traverse(node[2])
        right_type = self.traverse(node[3])
        
        if left_type == 'LOGICAL' or right_type == 'LOGICAL':
            print(f"Semantic Error: Invalid arithmetic operation between {left_type} and {right_type}")
            return 'UNKNOWN'
            
        if left_type == 'REAL' or right_type == 'REAL':
            return 'REAL'
        return 'INTEGER'
        
    def visit_relop(self, node):
        left_type = self.traverse(node[2])
        right_type = self.traverse(node[3])
        
        if left_type == 'LOGICAL' or right_type == 'LOGICAL':
            print(f"Semantic Error: Invalid relational operation between {left_type} and {right_type}")
            
        return 'LOGICAL'
        
    def visit_logop(self, node):
        left_type = self.traverse(node[2])
        right_type = self.traverse(node[3])
        if (left_type != 'LOGICAL' and left_type != 'UNKNOWN') or (right_type != 'LOGICAL' and right_type != 'UNKNOWN'):
            print(f"Semantic Error: Logical operators require LOGICAL operands, got {left_type} and {right_type}")
        return 'LOGICAL'
        
    def visit_not(self, node):
        t = self.traverse(node[1])
        if t != 'LOGICAL' and t != 'UNKNOWN':
            print(f"Semantic Error: .NOT. operator requires LOGICAL operand, got {t}")
        return 'LOGICAL'

    def visit_function_call(self, node):
        func_name = node[1]
        arguments = node[2]

        try:
            func_info = self.table.lookup(func_name)
            if func_info is None:
                raise SemanticError(f"Semantic Error: '{func_name}' is not a function or variable!")

            if func_info.get('nature') != 'function':
                if func_info.get('is_array'):
                    return func_info['type']
                else:
                    raise SemanticError(f"Semantic Error: '{func_name}' is not a function!")

            expected_arg_num = func_info['arg_num']
            actual_arg_num = len(arguments)

            if actual_arg_num != expected_arg_num:
                raise SemanticError(f"Semantic Error: '{func_name}' expects [{expected_arg_num}] arguments but got [{actual_arg_num}]!")

            for arg in arguments:
                self.traverse(arg)
                
            return func_info['type']
        except SemanticError as e:
            self.errors.append(str(e))
            return 'UNKNOWN'

def analyze_semantics(ast):
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
