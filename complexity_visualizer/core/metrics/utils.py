"""Utility functions for metric calculators."""


def is_class_node(node_name: str) -> bool:
    """
    Determine if a node represents a class (vs. a package).

    Uses Java naming conventions:
    - Classes start with uppercase letter (e.g., "MyClass", "UserService")
    - Packages start with lowercase letter (e.g., "com.example.adapter")

    Args:
        node_name: The fully qualified name of the node

    Returns:
        True if the node is a class, False if it's a package

    Examples:
        >>> is_class_node("com.example.MyClass")
        True
        >>> is_class_node("com.example.adapter")
        False
        >>> is_class_node("MyClass")
        True
        >>> is_class_node("adapter")
        False
    """
    if not node_name:
        return False

    # Get the last segment after the final dot
    last_segment = node_name.split(".")[-1]

    # Classes start with uppercase, packages with lowercase
    return last_segment[0].isupper() if last_segment else False
