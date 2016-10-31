def leading_space(line_content):
    """Returns a string representing the leading whitespace for the specified
    string."""
    return line_content[:len(line_content) - len(line_content.lstrip())]

def insert_line_in_file(filename, lineno, content):
    """Inserts the specified content in the file below lineno, taking into
    account the whitespace in front of the line that lineno."""
    with open(filename, "r") as file:
        contents = file.readlines()

    # this is beancount-specific: if the line has no whitespace in front of it,
    # use the whitespace of the following line, else use double the whitespace
    indention = leading_space(contents[lineno]) * 2 \
                if len(leading_space(contents[lineno])) > 0 \
                else leading_space(contents[lineno + 1])

    contents.insert(lineno + 1, '{}{}\n'.format(indention, content))

    with open(filename, "w") as file:
        contents = "".join(contents)
        file.write(contents)
