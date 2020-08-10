import jezik
import sys


lexer = jezik.Lexer()
parser = jezik.Parser()
itp = jezik.Interpreter()


def run_code(txt):
    try:
        tree = parser.parse(lexer.tokenize(txt))
        itp.run(tree)
        return True, None
    except (jezik.LexerError, jezik.SyntaxError, jezik.InterpreterError) as e:
        return False, e


if len(sys.argv) != 2:
    while True:
        txt = input(">>> ")

        if not txt:
            continue
            
        success, error = run_code(txt)
        if not success:
            print(error)
else:
    try:
        f = open(sys.argv[1], 'r')
    except FileNotFoundError:
        sys.stderr.write(f"File {sys.argv[1]} not found.\n")
        sys.exit(1)
    else:
        code = f.read()
        f.close()

        success, error = run_code(code)
        if not success:
            print(error)
