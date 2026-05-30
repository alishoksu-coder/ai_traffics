def check_brackets(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pairs = {'{': '}', '(': ')', '[': ']'}
    stacks = {k: [] for k in pairs.keys()}
    
    for i, char in enumerate(content):
        if char in pairs.keys():
            stacks[char].append(i)
        elif char in pairs.values():
            # Find which pair it belongs to
            opener = [k for k, v in pairs.items() if v == char][0]
            if not stacks[opener]:
                print(f"Extra closing {char} at index {i}")
            else:
                stacks[opener].pop()
    
    for opener, stack in stacks.items():
        if stack:
            print(f"Unclosed {opener} starting at indices: {stack}")
            lines = content.splitlines()
            for idx in stack:
                count = 0
                for line_no, line in enumerate(lines):
                    count += len(line) + 1
                    if count > idx:
                        print(f"Unclosed {opener} at line {line_no + 1}: {line.strip()}")
                        break

if __name__ == "__main__":
    check_brackets('mobile/traffic_app/lib/api.dart')
