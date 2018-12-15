def main():
    files_lines, files_content, uniq_fl = [], {}, {}
    while True:
        try:
            file, lineno = [[file, int(lineno)] for file, lineno in [input().split()]][0]
        except:
            break
        files_lines.append((file, lineno))
        if file not in uniq_fl:
            uniq_fl[file] = set()
        uniq_fl[file].add(lineno - 1)

    for filename in uniq_fl:
        files_content[filename] = {}
        uniq_lines = uniq_fl[filename]
        with open(filename, 'r') as s:
            for lineidx, line in enumerate(s):
                if lineidx not in uniq_lines:
                    continue
                files_content[filename][lineidx + 1] = line.strip()
                uniq_lines.remove(lineidx)
                if not uniq_lines:
                    break

    for file, lineno in files_lines:
        print(files_content[file][lineno])


if __name__ == '__main__':
    main()
