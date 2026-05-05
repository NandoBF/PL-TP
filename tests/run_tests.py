import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler import compile_file
from symbols import SemanticError

class TestCompiler(unittest.TestCase):
    def test_valid_files(self):
        valid_dir = 'tests/valid'
        for filename in os.listdir(valid_dir):
            if filename.endswith('.f'):
                filepath = os.path.join(valid_dir, filename)
                output_path = os.path.join(valid_dir, filename.replace('.f', '.vm'))
                try:
                    compile_file(filepath, output_path)
                    self.assertTrue(os.path.exists(output_path))
                except Exception as e:
                    self.fail(f"Valid file {filename} failed to compile: {e}")

    def test_invalid_syntax(self):
        syntax_dir = 'tests/invalid_syntax'
        for filename in os.listdir(syntax_dir):
            if filename.endswith('.f'):
                filepath = os.path.join(syntax_dir, filename)
                with self.assertRaises(SyntaxError, msg=f"File {filename} should have failed syntax analysis."):
                    compile_file(filepath)

    def test_invalid_semantic(self):
        semantic_dir = 'tests/invalid_semantic'
        for filename in os.listdir(semantic_dir):
            if filename.endswith('.f'):
                filepath = os.path.join(semantic_dir, filename)
                with self.assertRaises(SemanticError, msg=f"File {filename} should have failed semantic analysis."):
                    compile_file(filepath)

if __name__ == '__main__':
    unittest.main()
