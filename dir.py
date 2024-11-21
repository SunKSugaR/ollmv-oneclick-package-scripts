import subprocess, threading

def general_cmd(cmd: str | list, encoding: str = 'utf-8') -> tuple:
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return (output.decode(encoding=encoding,errors='ignore').strip(), error)

def pip_install(req_file: str):
    pass

print(general_cmd(['call', 'env-activate.bat', 'conda', 'pip']))