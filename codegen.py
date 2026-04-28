from symbols import SymbolTable


def generate_code(ast):
    table = SymbolTable()
    code = []

    label_counter = [0] # to control de IF labels

    def new_label():
        label_counter[0] += 1
        return f"L{label_counter[0]}"


    def emit(instruction):
        code.append(instruction)

    def traverse(node):
        if node is None:
            return

        if isinstance(node, list):
            for n in node:
                traverse(n)
            return
        
        node_type = node[0]
        if node_type == 'program':
            body = node[2]
            emit("START")
            traverse(body)
            emit("STOP")

        elif node_type == 'declare':
            data_type = node[1]
            variables = node[2]

            space_to_alloc = 0
            for var in variables:
                nature = var[0]
                name = var[1]

                if nature == 'array':
                    size = node[2]
                    table.declare(name, data_type, is_array=True, size=size)
                    space_to_alloc += size
                else:
                    table.declare(name, data_type)
                    space_to_alloc += 1

            if space_to_alloc > 0:
                emit(f"PUSHN {space_to_alloc}")

        elif node_type == 'assign':
            target_name = node[1][1]
            expression = node[2]

            traverse(expression)
            info = table.lookup(target_name)
            address = info['address']

            if info['is_global']:
                emit(f"STOREG {address}")
            else:
                emit(f"STOREL {address}")

        elif node_type == 'var_ref':
            var_name = node[1]
            info = table.lookup(var_name)
            address = info['address']

            if info['is_global']:
                emit(f"PUSHG {address}")
            else:
                emit(f"PUSHL {address}")

        elif node_type == 'num':
            value = node[1]
            emit(f"PUSHI {value}")

        elif node_type == 'binop':
            op = node[1]
            traverse(node[2])
            traverse(node[3])

            if op == '+': emit("ADD")
            elif op == '-': emit("SUB")
            elif op == '*': emit("MUL")
            elif op == '/': emit("DIV")

        elif node_type == 'labeled':
            label_num = node[1]
            instruction = node[2]

            emit(f"LABEL{label_num}:")
            traverse(instruction)

        elif node_type == 'goto':
            label_num = node[1]
            emit(f"JUMP LABEL{label_num}")

        elif node_type == 'relop':
            op = node[1]
            traverse(node[2])
            traverse(node[3])

            if op == '.GT.': emit("SUP")
            elif op == '.LT.': emit("INF")
            elif op == '.GE.': emit("SUPEQ")
            elif op == '.LE.': emit("INFEQ")
            elif op == '.EQ.': emit("EQUAL")
            elif op == '.NE.':
                emit("EQUAL")
                emit("NOT")

        elif node_type == 'if':
            cond = node[1]
            then_branch = node[2]
            else_branch = node[3]

            traverse(cond)
            if else_branch is None:
                # simple if
                end_label = new_label()
                emit(f"JZ {end_label}")
                traverse(then_branch)
                emit(f"{end_label}:")
            else:
                label_else = new_label()
                label_end = new_label()

                emit(f"JZ {label_else}")
                traverse(then_branch)
                emit(f"JUMP {label_end}")

                emit(f"{label_else}:")
                traverse(else_branch)
                emit(f"{label_end}:")

    traverse(ast)
    return "\n".join(code)
