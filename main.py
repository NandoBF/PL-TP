import sys
import os
from compiler import compile_file

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python main.py <source.f> [-o <output.vm>]")
        sys.exit(1)
        
    source = sys.argv[1]
    output = None
    if len(sys.argv) == 4 and sys.argv[2] == '-o':
        output = sys.argv[3]
    else:
        output = os.path.splitext(source)[0] + '.vm'
        
    try:
        compile_file(source, output)
        print(f"Compilation successful. Output written to {output}")
    except Exception as e:
        print(f"Compilation failed: {e}")
        sys.exit(1)
