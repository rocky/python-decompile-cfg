#/bin/bash
PYTHON_VERSION=3.8
decompile3_cfg_merge_38_owd=$(pwd)
cd $(dirname ${BASH_SOURCE[0]})
(cd .. && pyenv local $PYTHON_VERSION)
if . ./setup-python-3.8.sh; then
    git merge master
fi
cd $decompile3_cfg_merge_38_owd
