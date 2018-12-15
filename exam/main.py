files_content = dict()
files, lines = [], []

while True:
    try:
        item = input()
    except (EOFError, KeyboardInterrupt):
        break
    tmp = item.split()
    files.append(tmp[0])
    lines.append(int(tmp[1]))

uniq_files = set(files)

for filename in uniq_files:
    files_content[filename] = []
    tmp_lines = [lines[idx] - 1 for idx, file in enumerate(files) if file == filename]
    with open(filename, 'r') as s:
        for i, line in enumerate(s):
            if i in tmp_lines:
                tmp_lines.remove(i)
                files_content[filename].append((i + 1, line))
            if not tmp_lines:
                break

for idx, line_num in enumerate(lines):
    for file in files_content[files[idx]]:
        if file[0] == line_num:
            print(file[1].strip())
            break
