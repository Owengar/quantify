import os
import pathlib
import git
import update_interface



def open_vscode(open_folder):
    print(os.system(f"code {open_folder}"))



def check_for_updates(open_folder, source_dir):
    os.system(f"powershell -executionpolicy bypass -File {source_dir}\\git_initer.ps1")
    localcopy = git.Repo(open_folder)
    updates = localcopy.git.diff("main", "latest", "--", "source")
    if len(updates):
        while True:
            if update_interface.event_loop(updates):
                os.system("git checkout latest source")
                os.system("git commit -m update_commit")
                break


    os.system("git branch latest -D")


print("new update")
if __name__ == "__main__":

    open_folder = str(pathlib.Path().resolve())
    source_dir = open_folder + "\\source"
    check_for_updates(open_folder, source_dir)
    open_vscode(open_folder)


    print("main")
