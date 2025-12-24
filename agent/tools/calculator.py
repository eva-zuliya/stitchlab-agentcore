from strands import tool


@tool
def subtract(a: int, b: int) -> int:
    """Calculate the difference between two numbers"""
    return a - b

@tool
def multiply(a: int, b: int) -> int:
    """Calculate the product of two numbers"""
    return a * b