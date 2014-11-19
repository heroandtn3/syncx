import os

def scan_dir(src_path):
    """
    Scan for files in `src_path` directory

    Return a generator of file paths.
    """
    if not os.path.isdir(src_path):
        raise Exception('src_path does not contain working_dir')
    for dirpath, dirnames, filenames in os.walk(src_path):
        for f in filenames:
            yield os.path.join(dirpath, f)

if __name__ == '__main__':
    for f in scan_dir('conf'):
        print(f)
