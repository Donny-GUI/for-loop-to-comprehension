import ast
from typing import Optional, List, Set



def find_lists_that_append(forloop: ast.For) -> Set[str]:
    """
    Finds lists that are being appended to in a for loop.

    Args:
        forloop (ast.For): The Node to analyze.

    Returns:
        Set[str]: A set containing the names of the lists being appended to.
    """
    appended_lists: Set[str] = set()
    for subnode in forloop.body:
        if isinstance(subnode, ast.Expr) and isinstance(subnode.value, ast.Call):
            call = subnode.value
            if isinstance(call.func, ast.Attribute) and call.func.attr == 'append':
                if isinstance(call.func.value, ast.Name):
                    appended_lists.add(call.func.value.id)
    return appended_lists

def is_append(node: ast.AST) -> bool:
    """
    Checks if the given AST node represents an append operation.

    Args:
        node (ast.AST): The AST node to check.

    Returns:
        bool: True if the node represents an append operation, False otherwise.
    """
    if isinstance(node, ast.Expr) and \
        isinstance(node.value, ast.Call) and \
        isinstance(node.value.func, ast.Attribute) and \
        node.value.func.attr == 'append':
        return True
    return False

def if_has_append(node: ast.If) -> bool:
    """
    Checks if the given if statement contains an append operation.

    Args:
        node (ast.If): The if statement AST node to check.

    Returns:
        bool: True if the if statement contains an append operation, False otherwise.
    """
    for supernode in ast.walk(node):
        if is_append(supernode):
            return True
    return False

def ifs_with_appends(node: ast.For) -> List[ast.If]:
    """
    Finds all if statements with append operations within a for loop.

    Args:
        node (ast.For): The for loop AST node to analyze.

    Returns:
        List[ast.If]: A list of if statement AST nodes with append operations.
    """
    ifs = []
    for supernode in node.body:
        if isinstance(supernode, ast.If) and if_has_append(supernode):
            ifs.append(supernode)
    return ifs

def for_has_append(node: ast.For) -> bool:
    """
    Checks if the given for loop contains an append operation.

    Args:
        node (ast.For): The for loop AST node to check.

    Returns:
        bool: True if the for loop contains an append operation, False otherwise.
    """
    for supernode in ast.walk(node):
        if is_append(supernode):
            return True
    return False

def find_appends_at_base(node: ast.For) -> List[ast.Expr]:
    """
    Finds all append operations directly within the body of a for loop.

    Args:
        node (ast.For): The for loop AST node to analyze.

    Returns:
        List[ast.Expr]: A list of append operation AST nodes.
    """
    appends = []
    for subnode in node.body:
        if is_append(subnode):
            appends.append(subnode)
    return appends

def is_candidate_for_comprehension(node: ast.For) -> bool:
    """
    Checks if the given for loop is a candidate for conversion to a list comprehension.

    Args:
        node (ast.For): The for loop AST node to check.

    Returns:
        bool: True if the for loop is a candidate for conversion, False otherwise.
    """
    return isinstance(node, ast.For) and for_has_append(node)
def create_element_expr(node: ast.For) -> ast.AST:
    """
    Creates the element expression for the list comprehension.

    Args:
        node (ast.For): The for loop AST node.

    Returns:
        ast.AST: The element expression AST node.
    """
    # Collect used variable names in the loop body
    used_variables = set()
    for subnode in node.body:
        for name in ast.walk(subnode):
            if isinstance(name, ast.Name):
                used_variables.add(name.id)

    if isinstance(node.target, ast.Tuple):
        # If the target of the for loop is a tuple and both 'name' and 'age' are used,
        # return the tuple (name, age); otherwise, return just the variable being appended
        if 'name' in used_variables and 'age' in used_variables:
            return node.target
        else:
            for element in node.target.elts:
                if isinstance(element, ast.Name):
                    return ast.Name(id=element.id, ctx=ast.Load())
    else:
        # If the target is not a tuple, and the target name is used in the loop body, return the target name
        if node.target.id in used_variables:
            return ast.Name(id=node.target.id, ctx=ast.Load())

    return None  # Return None if it cannot determine the element expression

def for_loop_to_dict_comprehension(node: ast.For) -> Optional[ast.DictComp]:
    """
    Converts a for loop AST node into a dict comprehension.

    Args:
        node (ast.For): The for loop AST node.

    Returns:
        Optional[ast.DictComp]: The dict comprehension AST node, or None if conversion is not possible.
    """
    if not isinstance(node, ast.For):
        return None

    # Check if the loop body contains assignments to dictionary keys
    key_assignments = {}
    for subnode in node.body:
        if isinstance(subnode, ast.Assign) and len(subnode.targets) == 1 and isinstance(subnode.targets[0], ast.Subscript):
            target = subnode.targets[0]
            if isinstance(target.value, ast.Name) and target.value.id == 'result' and isinstance(target.slice, ast.Index) and isinstance(target.slice.value, ast.Str):
                key = target.slice.value.s
                if isinstance(subnode.value, ast.Name):
                    value = subnode.value.id
                    key_assignments[key] = value

    # If there are key assignments, construct the dict comprehension
    if key_assignments:
        generators = [ast.comprehension(target=node.target, iter=node.iter, ifs=[], is_async=False)]
        key_expr = ast.DictCompKey()
        value_expr = ast.DictCompValue()
        if_expr = None

        for key, value in key_assignments.items():
            key_expr.keys.append(ast.Constant(value=key))
            value_expr.values.append(ast.Name(id=value, ctx=ast.Load()))

        # Construct the dict comprehension node
        dict_comp = ast.DictComp(key=key_expr, value=value_expr, generators=generators, is_async=False)
        return dict_comp

    return None  # Return None if conversion is not possible
 
def for_loop_to_list_comprehension(node: ast.For) -> Optional[ast.ListComp]:
    """
    Converts a for loop AST node into a list comprehension.

    Args:
        node (ast.For): The for loop AST node.

    Returns:
        Optional[ast.ListComp]: The list comprehension AST node, or None if conversion is not possible.
    """
    if not is_candidate_for_comprehension(node):
        return None
    
    
    def create_generators(node: ast.For) -> list[ast.comprehension]:
        return [ast.comprehension(target=node.target, iter=node.iter, ifs=[], is_async=False)]

    loop_body = node.body

    # Construct the 'elt' (element) expression
    elt_expr = create_element_expr(node)
    generators = create_generators(node)

    # Construct the 'generators' (loops and conditions) for the list comprehension
    conditions = []

    for stmt in loop_body:
        if isinstance(stmt, ast.If) and if_has_append(stmt):
            conditions.append(stmt.test)

    if conditions:
        # If there are conditions, combine them with 'and'
        combined_condition = conditions[0]
        for condition in conditions[1:]:
            combined_condition = ast.BoolOp(op=ast.And(), values=[combined_condition, condition])
        generators[-1].ifs.append(combined_condition)

    # Handle else statement if present
    else_condition = None
    for stmt in loop_body:
        if isinstance(stmt, ast.If) and len(stmt.orelse) != 0:
            else_condition = ast.UnaryOp(op=ast.Not(), operand=combined_condition)

    if else_condition:
        # Construct else condition
        generators[-1].ifs.append(else_condition)

    # Construct the list comprehension node
    list_comp = ast.ListComp(elt=elt_expr, generators=generators)
    return list_comp

def determine_comprehension_type(node: ast.For) -> Optional[str]:
    """
    Determines if the given for loop is a list comprehension or a dictionary comprehension.

    Args:
        node (ast.For): The for loop AST node.

    Returns:
        Optional[str]: A string indicating the type of comprehension ('list' or 'dict'), 
                       or None if the loop is neither.
    """
    if not isinstance(node, ast.For):
        return None

    # Check if the loop body contains assignments to dictionary keys
    has_dict_assignment = False
    has_list_append = False
    for subnode in node.body:
        if isinstance(subnode, ast.Assign) and len(subnode.targets) == 1 and isinstance(subnode.targets[0], ast.Subscript):
            target = subnode.targets[0]
            if isinstance(target.value, ast.Name) and target.value.id == 'result' and isinstance(target.slice, ast.Index) and isinstance(target.slice.value, ast.Str):
                has_dict_assignment = True
        elif isinstance(subnode, ast.Expr) and isinstance(subnode.value, ast.Call):
            call = subnode.value
            if isinstance(call.func, ast.Attribute) and call.func.attr == 'append':
                if isinstance(call.func.value, ast.Name) and call.func.value.id == 'result':
                    has_list_append = True

    if has_dict_assignment:
        return 'dict'
    elif has_list_append:
        return 'list'
    else:
        return None


code = """
# For loop
squares = []
for i in range(1, 11):
    squares.append(i ** 2)

    
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
evens = []
for num in numbers:
    if num % 2 == 0:
        evens.append(num)

        
names = ['Alice', 'Bob', 'Charlie']
ages = [30, 25, 35]
people = []
for name, age in zip(names, ages):
    people.append((name, age))

text = "hello world"
unique_chars = []
for char in text:
    if char not in unique_chars:
        unique_chars.append(char)

        
names = ['Alice', 'Bob', 'Charlie']
ages = [30, 25, 35]
people = []
for name, age in zip(names, ages):
    people.append(age)


"""


tree = ast.parse(code)
for node in ast.walk(tree):
    if isinstance(node, ast.For):
        lc = for_loop_to_list_comprehension(node)
        print(ast.unparse(lc))
