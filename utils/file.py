import os


def mkdir(path):
    os.makedirs(path, exist_ok=True)


def mkfile(content, dir_path, file_name):
    mkdir(dir_path)
    file_path = os.path.join(dir_path, file_name)
    with open(file_path, "w", newline='\n') as f:
        f.write(content)
