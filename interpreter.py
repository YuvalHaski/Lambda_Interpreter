from ast_node import FunctionDefinition, LambdaExpression, FunctionApplication, Identifier, \
    IntegerLiteral, BooleanLiteral, UnaryOperation, BinaryOperation, IfStatement
from lexer import Lexer
from parser import Parser


class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.env = {}

    def get(self, name):
        print(f"DEBUG: Getting value of '{name}' from environment.")
        if name in self.env:
            return self.env[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise NameError(f"Undefined variable: {name}")

    def set(self, name, value):
        print(f"DEBUG: Setting '{name}' to '{value}' in environment.")
        self.env[name] = value

    def extend(self, names, values):
        print(f"DEBUG: Extending environment with {dict(zip(names, values))}.")
        child = Environment(self)
        for name, value in zip(names, values):
            child.set(name, value)
        return child


class Interpreter:
    def __init__(self, ast):
        self.ast = ast
        self.global_env = Environment()

    def interpret(self):
        print("DEBUG: Starting interpretation.")
        try:
            result = None
            for node in self.ast:
                result = self.eval(node, self.global_env)
                print(result)
            print("DEBUG: Interpretation finished.")
            return result
        except Exception as e:
            raise RuntimeError(f"Runtime error during interpretation: {str(e)}")

    def eval(self, node, env):
        print(f"DEBUG: Evaluating node {node} with environment {env.env}.")
        if isinstance(node, IntegerLiteral):
            print(f"DEBUG: IntegerLiteral with value {node.value}.")
            return node.value

        elif isinstance(node, BooleanLiteral):
            print(f"DEBUG: BooleanLiteral with value {node.value}.")
            return node.value

        elif isinstance(node, Identifier):
            return env.get(node.name)

        elif isinstance(node, BinaryOperation):
            print(f"DEBUG: BinaryOperation with operator '{node.operator}'.")
            left = self.eval(node.left, env)
            # For logical OR (||), short-circuit if left side is True
            if node.operator == '||' and left:
                return True
            # For logical AND (&&), short-circuit if left side is False
            if node.operator == '&&' and not left:
                return False
            right = self.eval(node.right, env)
            return self.apply_operator(node.operator, left, right)

        elif isinstance(node, UnaryOperation):
            print(f"DEBUG: UnaryOperation with operator '{node.operator}'.")
            value = self.eval(node.operand, env)
            return self.apply_unary_operator(node.operator, value)

        elif isinstance(node, FunctionDefinition):
            print(f"DEBUG: FunctionDefinition with name '{node.name}'.")
            env.set(node.name, (node.params, node.body, env))
            return None

        elif isinstance(node, LambdaExpression):
            print(f"DEBUG: LambdaExpression with params {node.params} and body {node.body}.")
            print('node.params:', node.params)
            return node.params, node.body, env

        elif isinstance(node, FunctionApplication):
            try:
                print(f"DEBUG: FunctionApplication with function {node.func} and args {node.args}.")

                # Check if the function is a string (indicating it's an identifier for a named function)
                if isinstance(node.func, str):
                    func = env.get(node.func)
                else:
                    func = self.eval(node.func, env)

                # Evaluate the arguments
                args = [self.eval(arg, env) for arg in node.args]

                # If the function is a regular function or lambda, apply the arguments
                if isinstance(func, tuple) and len(func) == 3:
                    params, body, closure_env = func

                    if isinstance(params, list):  # Regular function call
                        if len(params) != len(args):
                            raise TypeError(f"Function expected {len(params)} arguments but got {len(args)}")

                        new_env = closure_env.extend(params, args)
                        return self.eval(body, new_env)
                    else:  # Lambda expression
                        for arg in args:
                            func = self.apply_function(func, [arg])
                        return func

                else:
                    raise TypeError(f"Expected a function or lambda expression, but got: {func}")

            except Exception as e:
                raise RuntimeError(f"Error applying function: {str(e)}")

        elif isinstance(node, IfStatement):
            print(f"DEBUG: IfStatement with condition {node.condition}.")
            try:
                condition_value = self.eval(node.condition, env)
                if condition_value:
                    return self.eval(node.consequence, env)
                elif node.alternative is not None:
                    return self.eval(node.alternative, env)
                return None
            except Exception as e:
                raise RuntimeError(f"Error evaluating if-statement: {str(e)}")

        else:
            raise TypeError(f"Unknown node type: {type(node)}")

    def apply_function(self, func, args):
        print(f"DEBUG: Applying function with param '{func[0]}', body '{func[1]}', and arg '{args[0]}'.")

        param, body, closure_env = func

        if len(args) != 1:
            raise TypeError("Each lambda expression should receive exactly one argument.")

        new_env = closure_env.extend([param], args)
        result = self.eval(body, new_env)
        return result

    def apply_operator(self, op, left, right):
        print(f"DEBUG: Applying operator '{op}' with left '{left}' and right '{right}'.")
        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            if right == 0:
                raise ZeroDivisionError("Division by zero is not allowed")
            return left // right
        elif op == '%':
            return left % right
        elif op == '&&':
            return left and right
        elif op == '||':
            return left or right
        elif op == '==':
            return left == right
        elif op == '!=':
            return left != right
        elif op == '>':
            return left > right
        elif op == '<':
            return left < right
        elif op == '>=':
            return left >= right
        elif op == '<=':
            return left <= right
        else:
            raise TypeError(f"Unknown operator: {op}")

    def apply_unary_operator(self, op, value):
        print(f"DEBUG: Applying unary operator '{op}' with value '{value}'.")
        if op == '!':
            return not value
        else:
            raise TypeError(f"Unknown unary operator: {op}")



# code = """
# Defun {name: factorial, arguments: (n,)}
# (n == 0) || (n * factorial(n - 1))
# factorial(3)
# factorial(4)
#
# """
# (Lambd x. (Lambd y. (y+x)))(5,factorial(5))

# -------------- Examples Recursion: --------------- #

# Defun {name: factorial, arguments: (n,)}
# (n == 0) || (n * factorial(n - 1))
# factorial(5)

# Defun {name: sum_of_digits, arguments: (n,)}
# if (n == 0) {
#     False
# }
# else {
# n % 10 + sum_of_digits(n / 10)
# }
#
# sum_of_digits(1234)

# Defun {name: gcd, arguments: (a, b,)}
# if (b == 0) {
#     a
# } else {
#     gcd(b, a % b)
# }
#
# gcd(48, 18)

# Defun {name: power, arguments: (base, exponent,)}
# if (exponent == 0) {
#     1
# } else {
#     base * power(base, exponent - 1)
# }
#
# power(2, 3)


# --------- Example NOT ------------ #
# """Defun {name: factorial, arguments: (n,)}
# !(!(n > 6) && (n == 5))
# factorial(5)"""
#
#
#
#
#
#
#
#
#
# tokens = Lexer(code).tokenize()
# ast = Parser(tokens).parse()
# print(ast)
# interpreter = Interpreter(ast)
# result = interpreter.interpret()
# print(result)
#
#
#
# # Or to use the REPL:
# # interpreter.repl()