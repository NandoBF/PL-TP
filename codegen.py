from symbols import SymbolTable

class CodeGenerator:
    def __init__(self):
        self.table = SymbolTable()
        self.code = []
        self.label_counter = 0

    def new_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"

    def emit(self, instruction):
        self.code.append(instruction)

    def generate(self, ast):
        # Pre-register functions so they can be called before they are defined in code
        if isinstance(ast, list):
            for node in ast:
                if node[0] == 'function_def':
                    func_type = node[1]
                    func_name = node[2]
                    args = node[3]
                    self.table.declare_function(func_name, func_type, len(args))

        self.traverse(ast)
        return "\n".join(self.code)

    def traverse(self, node):
        if node is None:
            return

        if isinstance(node, list):
            for n in node:
                self.traverse(n)
            return
        
        node_type = node[0]
        method_name = f'visit_{node_type}'
        visitor = getattr(self, method_name, self.generic_visit)
        visitor(node)

    def generic_visit(self, node):
        raise Exception(f"No visit_{node[0]} method defined")

    def visit_program(self, node):
        body = node[2]
        self.emit("START")
        self.traverse(body)
        self.emit("STOP")

    def visit_block(self, node):
        body = node[1]
        self.traverse(body)

    def visit_nop(self, node):
        pass

    def visit_declare(self, node):
        data_type = node[1]
        variables = node[2]

        space_to_alloc = 0
        for var in variables:
            nature = var[0]
            name = var[1]

            if nature == 'array':
                # node[2] was incorrectly used in the original for size
                # var is ('array', 'name', size)
                size = var[2]
                self.table.declare(name, data_type, is_array=True, size=size)
                space_to_alloc += size
            else:
                self.table.declare(name, data_type)
                space_to_alloc += 1

        if space_to_alloc > 0:
            self.emit(f"PUSHN {space_to_alloc}")

    def visit_assign(self, node):
        target = node[1]
        expression = node[2]

        if target[0] == 'var_ref':
            target_name = target[1]
            self.traverse(expression)
            info = self.table.lookup(target_name)
            address = info['address']

            if info['is_global']:
                self.emit(f"STOREG {address}")
            else:
                self.emit(f"STOREL {address}")
        elif target[0] == 'array_ref':
            target_name = target[1]
            index_expr = target[2]
            
            info = self.table.lookup(target_name)
            address = info['address']
            
            # PUSH array base address
            if info['is_global']:
                self.emit("PUSHGP")
            else:
                self.emit("PUSHFP")
            self.emit(f"PUSHI {address}")
            self.emit("PADD")
            
            # PUSH index (Fortran arrays are 1-based, we make it 0-based for VM)
            self.traverse(index_expr)
            self.emit("PUSHI 1")
            self.emit("SUB")
            
            # PUSH value
            self.traverse(expression)
            
            self.emit("STOREN")

    def visit_var_ref(self, node):
        var_name = node[1]
        info = self.table.lookup(var_name)
        address = info['address']

        if info['is_global']:
            self.emit(f"PUSHG {address}")
        else:
            self.emit(f"PUSHL {address}")

    def visit_array_ref(self, node):
        target_name = node[1]
        index_expr = node[2]
        
        info = self.table.lookup(target_name)
        address = info['address']
        
        if info['is_global']:
            self.emit("PUSHGP")
        else:
            self.emit("PUSHFP")
        self.emit(f"PUSHI {address}")
        self.emit("PADD")
        
        self.traverse(index_expr)
        self.emit("PUSHI 1")
        self.emit("SUB")
        
        self.emit("LOADN")

    def visit_function_call(self, node):
        name = node[1]
        args = node[2]
        
        info = self.table.lookup(name)
        if info.get('nature') == 'variable' and info.get('is_array'):
            self.visit_array_ref(('array_ref', name, args[0]))
            return
            
        # Function Call:
        # 1. PUSHN 1 (Return value placeholder)
        self.emit("PUSHN 1")
        # 2. Push arguments
        for arg in args:
            self.traverse(arg)
        # 3. CALL
        self.emit(f"CALL FUNC_{name}")
        # 4. POP arguments
        if len(args) > 0:
            self.emit(f"POP {len(args)}")

    def visit_num(self, node):
        value = node[1]
        self.emit(f"PUSHI {value}")

    def visit_string(self, node):
        value = node[1]
        self.emit(f'PUSHS "{value}"')

    def visit_print(self, node):
        expressions = node[1]
        for expr in expressions:
            self.traverse(expr)
            if expr[0] == 'string':
                self.emit("WRITES")
            elif expr[0] == 'num':
                self.emit("WRITEI")
            elif expr[0] == 'var_ref':
                info = self.table.lookup(expr[1])
                if info['type'] == 'INTEGER':
                    self.emit("WRITEI")
                elif info['type'] == 'REAL':
                    self.emit("WRITEF")
            else:
                # Default to integer print for operations
                self.emit("WRITEI")
        self.emit("WRITELN")

    def visit_read(self, node):
        targets = node[1]
        for target in targets:
            if target[0] == 'var_ref':
                name = target[1]
                info = self.table.lookup(name)
                address = info['address']
                
                self.emit("READ")
                if info['type'] == 'INTEGER':
                    self.emit("ATOI")
                elif info['type'] == 'REAL':
                    self.emit("ATOF")
                
                if info['is_global']:
                    self.emit(f"STOREG {address}")
                else:
                    self.emit(f"STOREL {address}")

    def visit_binop(self, node):
        op = node[1]
        self.traverse(node[2])
        self.traverse(node[3])

        if op == '+': self.emit("ADD")
        elif op == '-': self.emit("SUB")
        elif op == '*': self.emit("MUL")
        elif op == '/': self.emit("DIV")

    def visit_do(self, node):
        # ('do', label, iterator_name, start_expr, end_expr)
        label_num = node[1]
        iter_name = node[2]
        start_expr = node[3]
        end_expr = node[4]
        
        info = self.table.lookup(iter_name)
        address = info['address']
        
        # Assign start_expr to iter
        self.traverse(start_expr)
        if info['is_global']:
            self.emit(f"STOREG {address}")
        else:
            self.emit(f"STOREL {address}")
            
        # We need a label to loop back to
        loop_start = self.new_label()
        self.emit(f"{loop_start}:")
        
        if not hasattr(self, 'do_loops'):
            self.do_loops = {}
        self.do_loops[label_num] = {
            'iter_name': iter_name,
            'end_expr': end_expr,
            'start_label': loop_start
        }

    def visit_function_def(self, node):
        func_type = node[1]
        func_name = node[2]
        args = node[3]
        body = node[4]
        
        self.emit(f"FUNC_{func_name}:")
        self.table.enter_scope()

        # The return value will be stored at fp[-len(args)]
        self.table.declare(func_name, func_type)
        self.table.lookup(func_name)['address'] = -len(args)
        
        # Local variables pushed after CALL start at fp[1]
        # We manually adjust the internal offset of the SymbolTable
        self.table._SymbolTable__local_offset = 1
        
        for instr in body:
            self.traverse(instr)
            if instr[0] == 'declare':
                for var in instr[2]:
                    name = var[1]
                    if name in args:
                        arg_index = args.index(name)
                        offset_from_fp = arg_index - len(args) + 1
                        
                        local_address = self.table.lookup(name)['address']
                        
                        self.emit(f"PUSHL {offset_from_fp}")
                        self.emit(f"STOREL {local_address}")
        
        self.table.exit_scope()

    def visit_return(self, node):
        self.emit("RETURN")

    def visit_labeled(self, node):
        label_num = node[1]
        instruction = node[2]

        self.emit(f"LABEL{label_num}:")
        
        if instruction == 'continue' or (isinstance(instruction, tuple) and instruction[0] == 'continue'):
            if hasattr(self, 'do_loops') and label_num in self.do_loops:
                loop_info = self.do_loops[label_num]
                iter_name = loop_info['iter_name']
                end_expr = loop_info['end_expr']
                start_label = loop_info['start_label']
                
                info = self.table.lookup(iter_name)
                address = info['address']
                
                # iter = iter + 1
                if info['is_global']:
                    self.emit(f"PUSHG {address}")
                else:
                    self.emit(f"PUSHL {address}")
                self.emit("PUSHI 1")
                self.emit("ADD")
                if info['is_global']:
                    self.emit(f"STOREG {address}")
                else:
                    self.emit(f"STOREL {address}")
                
                # Check if iter <= end_expr
                if info['is_global']:
                    self.emit(f"PUSHG {address}")
                else:
                    self.emit(f"PUSHL {address}")
                self.traverse(end_expr)
                self.emit("INFEQ")
                
                skip_jump = self.new_label()
                self.emit(f"JZ {skip_jump}")
                self.emit(f"JUMP {start_label}")
                self.emit(f"{skip_jump}:")
                
                del self.do_loops[label_num]
        else:
            self.traverse(instruction)

    def visit_goto(self, node):
        label_num = node[1]
        self.emit(f"JUMP LABEL{label_num}")

    def visit_relop(self, node):
        op = node[1]
        self.traverse(node[2])
        self.traverse(node[3])

        if op == '.GT.': self.emit("SUP")
        elif op == '.LT.': self.emit("INF")
        elif op == '.GE.': self.emit("SUPEQ")
        elif op == '.LE.': self.emit("INFEQ")
        elif op == '.EQ.': self.emit("EQUAL")
        elif op == '.NE.':
            self.emit("EQUAL")
            self.emit("NOT")

    def visit_bool(self, node):
        value = node[1]
        if value:
            self.emit("PUSHI 1")
        else:
            self.emit("PUSHI 0")

    def visit_not(self, node):
        self.traverse(node[1])
        self.emit("NOT")

    def visit_logop(self, node):
        op = node[1]
        self.traverse(node[2])
        self.traverse(node[3])
        if op == '.AND.':
            self.emit("AND")
        elif op == '.OR.':
            self.emit("OR")


    def visit_if(self, node):
        cond = node[1]
        then_branch = node[2]
        else_branch = node[3]

        self.traverse(cond)
        if else_branch is None:
            # simple if
            end_label = self.new_label()
            self.emit(f"JZ {end_label}")
            self.traverse(then_branch)
            self.emit(f"{end_label}:")
        else:
            label_else = self.new_label()
            label_end = self.new_label()

            self.emit(f"JZ {label_else}")
            self.traverse(then_branch)
            self.emit(f"JUMP {label_end}")

            self.emit(f"{label_else}:")
            self.traverse(else_branch)
            self.emit(f"{label_end}:")

def generate_code(ast):
    generator = CodeGenerator()
    return generator.generate(ast)
