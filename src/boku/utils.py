# UTILS
#


def frame(message: str, padding: int = 2) -> str:
    """Decorative frame around a message"""
    chars = "╭╮╰╯─│"
    message_lines = message.split("\n")
    longest_line = max(len(line) for line in message_lines)
    straight_length = longest_line + padding * 2
    lines = [
        f"{chars[5]}{' ' * padding}{line.strip().center(longest_line)}{' '*padding}{chars[5]}"
        for line in message_lines
    ]
    _message = [
        f"{chars[0]}{chars[4]*straight_length}{chars[1]}",
    ]
    _message.extend(lines)
    _message.append(f"{chars[2]}{chars[4]*straight_length}{chars[3]}")
    messages = "\n".join(_message)
    return messages


def yaml_suffixer(taskfile: str) -> str:
    """Add .yaml suffix to taskfile if not present"""
    if not taskfile.endswith((".yaml", ".yml")):
        return f"{taskfile}.yaml"
    return taskfile


HELPERS_YAML = """
helpers:
    ntfy:
        description: Send a notification to a NTFY host
        run: |
            curl \
            -H "Authorization: Bearer <token>" \
            -d "<message>" \
            <host>
        args:
            - token
            - message
            - host
  """
