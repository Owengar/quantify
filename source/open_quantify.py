import os
import pathlib
import git




def open_vscode(open_folder):
    if os.system(f"code {open_folder}") == 1:
        import update_interface
        update_interface.install_vscode()


    print(os.system(f"code {open_folder}"))
    print(os.system("whawfwfe"))



def check_for_updates(open_folder, source_dir):
    os.system(f"powershell -executionpolicy bypass -File {source_dir}\\git_initer.ps1")
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


    os.system("git branch latest -D")
    return



if __name__ == "__main__":

    open_folder = str(pathlib.Path().resolve())
    source_dir = open_folder + "\\source"
    check_for_updates(open_folder, source_dir)
    open_vscode(open_folder)


    print("main")
