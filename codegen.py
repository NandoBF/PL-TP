from symbols import SymbolTable


def generate_code(ast):
    table = SymbolTable()
    code = []

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

    traverse(ast)
    return "\n".join(code)
