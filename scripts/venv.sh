#!/bin/sh -x

quit(){
    if [ $# -gt 1 ];
    then
        echo "$1"
        shift
    fi
    exit $1
}

if [ -f ~/.dotfiles/virtualenvwrapperrc ];
then
    . ~/.dotfiles/virtualenvwrapperrc
fi

mkvirtualenv -r ./venv-reqs.txt "vmware_static_dhcp" || quit "Unable to make virtual environment." 1
