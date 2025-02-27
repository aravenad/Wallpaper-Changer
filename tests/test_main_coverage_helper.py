def create_test_values():
    """Create test values for use in tests to avoid StopIteration issues."""
    # Create a much larger list of values to prevent StopIteration
    return {
        'exit_flags': [False] * 995 + [True] * 5  # Set exit flag after 995 iterations
    }
    
def constant_time():
    """Return a constant time value."""
    return 100
