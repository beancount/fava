def uniquify(seq):
    """Removes duplicate items from a list whilst preserving order. """
    seen = set()
    if not seq:
        return []
    return [x for x in seq if x not in seen and not seen.add(x)]
