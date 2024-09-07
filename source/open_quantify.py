import os
import pathlib
import git
import git.cmd
import git.diff



def open_vscode(open_folder):
    print(os.system(f"code {open_folder}"))



def check_for_updates(open_folder, source_dir):
    os.system(f"powershell -executionpolicy bypass -File {source_dir}\\git_initer.ps1")
    localcopy = git.Repo(open_folder)
    print(localcopy.git.diff("localcopy", "latest", "--", "source"))
    """ latest, localcopy_branch = localcopy.branches[0], localcopy.branches[1]

    diffs = latest.commit.diff(localcopy_branch.commit)
    for diff in diffs:
        print(diff) """
    


if __name__ == "__main__":


    open_folder = str(pathlib.Path().resolve())
    source_dir = open_folder + "\\source"
    check_for_updates(open_folder, source_dir)
    open_vscode(open_folder)


    print("main")
