import unittest
from LexicalAnalyzer.Lexer import Lexer

class TestLexer(unittest.TestCase):
    def test_valid_tokens(self):
        lexer = Lexer()
        tokens, errors = lexer.tokenize("entero edad = 18")
        self.assertEqual(len(tokens), 3)
        self.assertEqual(len(errors), 0)

if __name__ == "__main__":
    unittest.main()
