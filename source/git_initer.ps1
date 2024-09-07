cd .\source

git init -b localcopy
git switch localcopy
git add .
git switch localcopy
git commit -m temporary
git fetch git@github.com:Owengar/quantify.git main:latest