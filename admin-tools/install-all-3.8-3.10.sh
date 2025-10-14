#!/usr/bin/bash
PACKAGE_MODULE=decompile_cfg
decompile_cfg_owd=$(pwd)
bs=${BASH_SOURCE[0]}
mydir=$(dirname $bs)
decompile_cfg_fulldir=$(readlink -f $mydir)
cd $decompile_cfg_fulldir
. ./checkout_common.sh

pyenv_file="pyenv-3.8-3.10-versions"
if ! source $pyenv_file ; then
    echo "Having trouble reading ${pyenv_file} version $(pwd)"
    exit 1
fi

source ${decompile_cfg_fulldir}/../${PACKAGE_MODULE}/version.py
if [[ ! $__version__ ]] ; then
    echo "Something is wrong: __version__ should have been set."
    exit 1
fi

cd ${decompile_cfg_fulldir}/../dist/

install_check_command="decompile-cfg --version"
install_file="decompile_cfg_38-${__version__}.tar.gz"
for pyversion in $PYVERSIONS; do
    echo "*** Installing ${install_file} for Python ${pyversion} ***"
    pyenv local $version
    pip install $install_file
    $install_check_command
    echo "----"
done
