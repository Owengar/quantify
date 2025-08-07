import json, sys, os



replacements = {
    "${fileDirname}" : sys.argv[1],
    "${fileBasenameNoExtension}" : sys.argv[2],
    "${allCppFiles}" : os.popen("powershell ; (Get-ChildItem -Filter '*.cpp').Name").read().replace("\n", " ")
}


command_string = "g++"

build_args = json.load(open(".vscode\\build_args.json", "r"))
for arg in build_args["args"]:
    for replacement in replacements:
        arg = arg.replace(replacement, replacements[replacement])
    command_string += f" {arg}"
print("\n\n")
print("its weird if this is printed")
print(command_string)
os.popen(command_string)
