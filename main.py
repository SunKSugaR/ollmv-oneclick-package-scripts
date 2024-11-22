import subprocess, re, yaml, os, psutil

# 使用 Windows下的pause和cls命令
if os.name == "nt":
    def pause_and_clear() -> None:
        os.system("pause")
        os.system("cls")
    def clear() -> None:
        os.system("cls")
else:
    print("请使用Windows系统运行本程序/Please run this program on Windows")
    exit()

# 加载语言配置
def load_languages(yamlfile: str, lang: str) -> dict:
    langs = ['zh', 'en']
    if lang not in langs:
        print("语言应该是以下之一/Language should be one of the following: ")
        print(langs)
        return None
    with open(yamlfile, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        return config[lang]

# 多消息打印
def multi_msg_print(messages: list) -> None:
    for msg in messages:
        print(msg)

# 通用命令执行器
def general_cmd(cmd: str | list, encoding: str = 'utf-8') -> tuple:
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return (output.decode(encoding=encoding,errors='ignore').strip(), error)

# 通过进程名获取PID
def get_pid_by_name(process_name: str):
    pid = None
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if proc.info['name'] == process_name:
            pid = proc.info['pid']
            break
    return pid

# 杀死进程
def kill_process(pid: int) -> bool:
    try:
        process = psutil.Process(pid)
        process.kill()
        return True
    except:
        return False

# 获取系统变量
def get_sysvar_Path() -> list:
    return general_cmd("echo %PATH%")[0].split(";")

# 从系统变量中获取CUDA路径
def get_cuda_paths() -> list:
    cuda_paths = []
    for path in get_sysvar_Path():
        if re.search("[C][U][D][A]", path) and (re.search("[b][i][n]", path) or re.search("[l][i][b][\\\\]", path)):
            if path not in cuda_paths:
                cuda_paths.append(path)
    return cuda_paths

# 获取用户变量
def get_user_vars() -> dict:
    user_vars = {}
    lines = general_cmd(["reg", "query", "HKEY_CURRENT_USER\\Environment"])[0].split("\n")
    for line in lines:
        result = line.strip().split("    ")
        if result in [['HKEY_CURRENT_USER\\Environment'],['']]:
            continue
        user_vars[result[0]] = result[2]
    return user_vars

# Conda环境检查
def have_conda() -> bool:
    if general_cmd("where conda")[0] == "":
        return False
    else:
        return True

def path_check(path: str, errmsg: str) -> bool:
    if os.path.exists(path):
        return True
    else:
        try:
            os.makedirs(path)
            return True
        except:
            print(errmsg)
            return False

# 主程序
if __name__ == "__main__":
    current_path = os.path.dirname(os.path.abspath(__file__))
    language = str(input("请选择语言/Please select language (zh/en): "))
    pause_and_clear()
    messages = load_languages("languages.yaml", language)
    if messages is None:
        pause_and_clear()
        exit()
    
    
    
    # 阶段一：环境检测
    # 选择部署虚拟环境的工具
    while True:
        print(messages['info']['stage_1'])
        multi_msg_print(messages['info']['venv_tools_requirements'])
        venv_tool = str(input(messages['info']['select_venv_tool']))
        
        if venv_tool == "conda":
            # Conda环境检查
            if not have_conda():
                print(messages['error']['conda_not_found'])
                print(messages['info']['venv_tool_reselect'])
                pause_and_clear()
                continue
            break
        elif venv_tool == "venv":
            # Python版本检查
            python_ver = general_cmd(["python", "--version"])[0].split()[1]
            if python_ver > "3.11.10" or python_ver < "3.10.0":
                print(messages['error']['python_version_not_supported'])
                print(messages['info']['current_python_version'].format(python_version=python_ver))
                print(messages['info']['venv_tool_reselect'])
                pause_and_clear()
                continue
            break
        elif venv_tool == "skip":
            venv_tool = None
            break
        else:
            print(messages['error']['invalid_input'])
            pause_and_clear()
            continue
        
    print(messages['info']['venv_tool_selected'].format(venv_tool=venv_tool))
    pause_and_clear()


    # CUDA&CUDNN环境检查
    print(messages['info']['stage_1'])
    defalut_cuda_path = "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA"
    cuda_paths = get_cuda_paths()
    if cuda_paths == [] or len(cuda_paths) < 2:
        if os.path.exists(defalut_cuda_path):
            print(messages['warning']['cuda_path_variable_not_set'])
        print(messages['warning']['cuda_not_found'])
        print(messages['info']['cuda_install_hint'])
    else:
        cudnn = False
        for path in cuda_paths:
            if os.path.exists(os.path.join(path, "cudnn.lib")):
                cudnn = True
                break
        if cudnn:
            print(messages['info']['cuda_found'].format(cuda_paths=cuda_paths))
        else:
            print(messages['warning']['cudnn_not_found'])
            print(messages['info']['cuda_install_hint'])
    pause_and_clear()
    
    
    # pip 镜像源检查与设置
    offical = "https://pypi.org/simple"
    def select_pip_repository(arepos: list, hint: str, pcrepo: str) -> str:
        repository = offical
        while True:
            print(messages['info']['stage_1'])
            if pcrepo != offical:
                print(messages['info']['pip_repository_found'].format(repository=pip_repository))
            pcrepo = messages['info']['official_repository'] if pcrepo == "" else pcrepo
            print(messages['info']['pip_current_repository'].format(repository=pcrepo))
            print(messages['warning']['pip_repository_warn'])
            multi_msg_print(arepos)
            try:
                index_of_repo = str(input(messages['info'][hint]))
                index_of_repo = int(index_of_repo) if index_of_repo.isdigit() else -1
                if index_of_repo == -1:
                    repository = offical if pcrepo == offical else pcrepo
                    return repository
            except Exception as e:
                print(messages['error']['invalid_input'], e)
                pause_and_clear()
                continue
            for repo in arepos:
                for index, url in repo.items():
                    if index == index_of_repo:
                        repository = url.split("：")[1]
                        return repository
            print(messages['error']['invalid_input'])
            pause_and_clear()
            continue
    
    pip_repository = general_cmd(["pip", "config", "get", "global.index-url"])[0]
    clear()
    available_repositorys = messages['info']['pip_repositorys']
    if pip_repository == "https://pypi.org/simple":
        pip_repository = select_pip_repository(available_repositorys, 'select_pip_repository', pip_repository)
    else:
        pip_repository = select_pip_repository(available_repositorys,'change_pip_repository', pip_repository)
        
    general_cmd(["pip", "config", "set", "global.index-url", pip_repository])
    print(messages['info']['pip_repository_set'].format(repository=pip_repository))
    pause_and_clear()
    
    
    # Ollama 安装检测
    print(messages['info']['stage_1'])
    ollama_app_path = general_cmd('where "ollama app"')[0]
    if ollama_app_path == "":
        print(messages['ollama']['not_found'])
        pause_and_clear()
        while True:
            print(messages['info']['stage_1'])
            ollama_install_path = str(input(messages['ollama']['install_path']))
            if ollama_install_path != "":
                if path_check(ollama_install_path, messages['error']['path_failed'].format(path=ollama_install_path)):
                    general_cmd(['external\\OllamaSetup.exe','/DIR="{}"'.format(ollama_install_path)])
                else:
                    continue
                ollama_app_path = os.path.join(ollama_install_path, "ollama app.exe")
                break
            else:
                general_cmd(['OllamaSetup.exe'])
                ollama_app_path = general_cmd('where "ollama app"')[0]
                break
    print(messages['ollama']['found'].format(path=ollama_app_path))
    
    # Ollama模型目录检测
    ollama_app_pid = get_pid_by_name("ollama app.exe")
    ollama_pid = get_pid_by_name("ollama.exe")
    pids = [["ollama app.exe", ollama_app_pid], ["ollama.exe", ollama_pid]]
    for pid in pids:
        if pid[1] is not None:
            print(messages['ollama']['running'].format(app=pid[0], pid=pid[1]))
            kill_process(pid[1])
            print(messages['ollama']['killed'].format(app=pid[0], pid=pid[1]))
    
    print(messages['ollama']['find_llms_path'])
    LLMs_path = get_user_vars().get('OLLAMA_MODELS')
    
    # 未找到模型目录，是否设置
    if LLMs_path is None:
        print(messages['ollama']['models_path_not_set'])
        while True:
            multi_msg_print(messages['ollama']['default_hints'])
            LLMs_path = str(input(messages['ollama']['select_or_default']))
            if LLMs_path == "":
                LLMs_path = os.path.join(current_path, "external\\LLMs")
                path_check(LLMs_path, messages['error']['path_failed'].format(path=LLMs_path))
                break
            else:
                if not path_check(LLMs_path, messages['error']['path_failed'].format(path=LLMs_path)):
                    continue
                break
    # 找到目录，是否需要更改
    else:
        print(messages['ollama']['models_path_found'].format(path=LLMs_path))
        print(messages['ollama']['found_hint'])
        while True:
            change_path = str(input(messages['ollama']['change_path']))
            if change_path != "":
                if path_check(change_path, messages['error']['path_failed'].format(path=change_path)):
                    LLMs_path = change_path
                    break
                else:
                    continue
            break
    
    # 设置 OLLAMA_MODELS 用户变量
    general_cmd(["setx", "OLLAMA_MODELS", LLMs_path])
    print(messages['ollama']['models_path_set'].format(path=LLMs_path))
    
    # 重新启动 Ollama 注意：ollama app.exe 启动后会自动启动 ollama.exe
    print(messages['ollama']['restart']) 
    subprocess.Popen(f'"{ollama_app_path}"')
    ollama_app_pid = get_pid_by_name("ollama app.exe")
    print(messages['ollama']['running'].format(app="ollama app.exe", pid=ollama_app_pid))
    pause_and_clear()
    
    
    # ffmpeg 安装检测
    print(messages['info']['stage_1'])
    ffmpeg_path = general_cmd('where ffmpeg')[0]
    if ffmpeg_path == '':
        print(messages['ffmpeg']['not_found'])
        pause_and_clear()
        while True:
            print(messages['info']['stage_1'])
            print(messages['ffmpeg']['setup_hint'])
            setup = str(input(messages['ffmpeg']['setup']))
            if setup == "y":
                ffmpeg_path = os.path.join(current_path, "external\\FFmpeg\\bin")
                general_cmd(['setx', 'Path', f"%PATH%;{ffmpeg_path}", '/m'])
                print(messages['ffmpeg']['path_set'].format(path=ffmpeg_path))
                break
            elif setup == "n":
                print(messages['ffmpeg']['not_setup'])
                break
            else:
                print(messages['error']['invalid_input'])
                pause_and_clear()
                continue
    else:
        print(messages['ffmpeg']['found'].format(path=ffmpeg_path))
    pause_and_clear()



    # 阶段二：依赖安装
    # 创建并激活虚拟环境
    venv_path = os.path.join(current_path, "ollmv-env")
    print(messages['info']['stage_2'])
    print(messages['info']['venv_tool_selected'].format(venv_tool=venv_tool))
    print(messages['info']['preparing_venv'])
    
    if os.path.exists(venv_path):
        pass
    if venv_tool == "conda":
        general_cmd(['conda', 'env', 'create', '-f', 'env.yaml', '-p', venv_path])
    elif venv_tool == "venv":
        general_cmd(['python', '-m', 'venv', 'ollmv-env'])
        venv_path = os.path.join(venv_path, "Scripts")
    else:
        print(messages['info']['venv_create_skipped'])
        
    python_path = os.path.join(venv_path, "python.exe")
    print(messages['info']['venv_created'])
    pause_and_clear()
    
    
    # 安装项目依赖
    print(messages['info']['stage_2'])
    print(messages['info']['installing_dependencies'])
    general_cmd([python_path, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    print(messages['info']['install_completed'])
    pause_and_clear()
    
    
    # 安装 MeloTTS
    print(messages['info']['stage_2'])
    print(messages['info']['installing_melotts'])
    melotts_path = os.path.join(current_path, "external\\MeloTTS")
    general_cmd([python_path, '-m', 'pip', 'install', '-e', melotts_path, '--no-warn-script-location', '--use-pep517'])
    print(messages['info']['install_completed'])
    multi_msg_print(messages['info']['unidic_download'])
    pause_and_clear()
    proxy = ""
    while True:
        print(messages['info']['stage_2'])
        proxy = str(input(messages['info']['set_proxy']))
        if proxy != "":
            if "127.0.0.1:" in proxy or "localhost:" in proxy:
                break
            else:
                print(messages['error']['invalid_proxy'])
                pause_and_clear()
                continue
        else:
            print(messages['info']['proxy_skipped'])
            break
    general_cmd(['unidicdl', python_path, proxy])
    pause_and_clear()
    
    
    # 以防万一，升级 edgeTTS
    print(messages['info']['stage_2'])
    print(messages['info']['upgrading_edgetts'])
    general_cmd([python_path, '-m', 'pip', 'install', '-U', 'edge-tts', '--no-warn-script-location'])
    print(messages['info']['install_completed'])
    pause_and_clear()
    
    
    
    # 阶段三：启动！
    print(messages['info']['stage_3'])
    general_cmd(['start', 'cmd', '/c', python_path, 'server.py'])
    