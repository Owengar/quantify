import os
import pathlib
import git
import subprocess




def open_vscode(open_folder):
    try:
        subprocess.call(f"code {open_folder}", creationflags=subprocess.CREATE_NO_WINDOW, shell=True)
    except:
        import update_interface
        update_interface.install_vscode()
    """ if os.system(f"code {open_folder}") == 1:
        import update_interface
        update_interface.install_vscode() """




def check_for_updates(open_folder, source_dir):
    subprocess.call(f"powershell -executionpolicy bypass -File {source_dir}\\git_initer.ps1", creationflags=subprocess.CREATE_NO_WINDOW)
    subprocess.call(f"powershell -executionpolicy bypass -File {source_dir}\\git_initer.ps1", creationflags=subprocess.CREATE_NO_WINDOW)
    localcopy = git.Repo(open_folder)
    updates = localcopy.git.diff("main", "latest", "--", "source")
    if len(updates):
        import update_interface
        while True:
            up_return = update_interface.event_loop(updates)
            if up_return == 1:
                os.system("git checkout latest source")
                os.system("git commit -m update_commit")
                update_interface.finished()
                break
            elif up_return == 2:
                break


    subprocess.call("git branch latest -D", creationflags=subprocess.CREATE_NO_WINDOW)
    return




if __name__ == "__main__":

    source_dir = str(pathlib.Path().resolve())
    open_dir = source_dir.removesuffix("\\source")
    check_for_updates(open_dir, source_dir)
    open_vscode(open_dir)
