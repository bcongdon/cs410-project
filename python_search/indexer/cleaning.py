def clean_message(message):
    lines = message.split('\n')

    # Remove quoted text from messages
    l_idx = 0
    while l_idx + 1 < len(lines):
        line, next_line = lines[l_idx], lines[l_idx + 1]
        if next_line.strip().startswith('>'):
            lines.pop(l_idx)
            while l_idx < len(lines) and lines[l_idx].strip().startswith('>'):
                lines.pop(l_idx)
        # Remove attachment messages from messages
        elif line.strip() in ['--', '-------------- next part --------------']:
            lines = lines[:l_idx]
            break
        else:
            l_idx += 1
    return '\n'.join(lines)


if __name__ == '__main__':
    test_document = 'start\nQuote Header\n>quote\n>quote\nNot Quoted'
    assert clean_message(test_document) == 'start\nNot Quoted'
