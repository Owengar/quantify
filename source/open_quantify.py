import os
import pathlib
import git
import subprocess
import sys
import zipfile
import win32com.client 
import site



def unzip_dependencies(install_dir):
    site_packages_path = site.getsitepackages()[1]



    zip_dependency_path = install_dir + "\\source\\zip_dependency.zip"

    with zipfile.ZipFile(zip_dependency_path, "r") as zipped_dependencies:
        zipped_dependencies.extractall(path=site_packages_path)

def resource_path(relative_path, return_base_path = False):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    if return_base_path:
        return base_path
    return os.path.join(base_path, relative_path)


def open_vscode(open_folder):
    try:
        subprocess.call(f"code {open_folder}", creationflags=subprocess.CREATE_NO_WINDOW, shell=True)
    except:
        import update_interface
        update_interface.install_vscode()





def check_for_updates(open_folder, source_dir):
    #subprocess.call(f"powershell -executionpolicy bypass -File {resource_path("git_initer.ps1")}", creationflags=subprocess.CREATE_NO_WINDOW)
    subprocess.run(f"cd {open_folder} & git init -b main & git switch main & git add . & git commit -m pre_update_commit & git fetch git@github.com:Owengar/quantify.git main:latest", creationflags=subprocess.CREATE_NO_WINDOW, shell=True)
    localcopy = git.Repo(open_folder)
    updates = localcopy.git.diff("main", "latest", "--", "source")
    if len(updates):
        import update_interface
        while True:
            up_return = update_interface.event_loop(updates, open_folder)
            if up_return == 1:
                subprocess.run(f"cd {open_folder} & git checkout latest source & git commit -m update_commit", creationflags=subprocess.CREATE_NO_WINDOW, shell=True)
                unzip_dependencies(open_folder)
                update_interface.finished()
                break
            elif up_return == 2:
                break


    subprocess.run(f"cd {open_folder} & git branch latest -D", creationflags=subprocess.CREATE_NO_WINDOW, shell=True)
    return




if __name__ == "__main__":
    source_dir = ""
    for file in os.listdir():
        if file.endswith(".lnk"):
            try:
                link_path = os.path.abspath(file)
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(link_path)
                sc_target = shortcut.Targetpath
                if sc_target.endswith("open_quantify.exe"):
                    source_dir = sc_target.removesuffix("\\open_quantify.exe")
                    break
            except:
                pass
    if not source_dir:
        for file in os.listdir("C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs"):
            if file.endswith(".lnk"):
                try:
                    link_path = "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\" + file
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shortcut = shell.CreateShortCut(link_path)
                    sc_target = shortcut.Targetpath
                    if sc_target.endswith("open_quantify.exe"):
                        source_dir = sc_target.removesuffix("\\open_quantify.exe")
                        break
                except:
                    pass
    if not source_dir:
        source_dir = str(pathlib.Path().resolve())
    print(source_dir)
    open_dir = source_dir.removesuffix("\\source")
    check_for_updates(open_dir, source_dir)
    open_vscode(open_dir)
