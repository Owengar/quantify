function ReConfigureVenv()
{
    cd ~
    $pypath = (Get-Command python).Path
    $parent = Split-Path -Path $pypath -Parent
    python $PSScriptRoot\rewrite_pyvenv_cfg.py $parent
    cd $PSScriptRoot
    cd ..
    cd ..
} 

ReConfigureVenv