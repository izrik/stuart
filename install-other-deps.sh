#!/usr/bin/env bash -xe

if [[ "$(uname)" = "Darwin" ]]; then
    brew install shellcheck
elif [[ "$(uname)" = "Linux" ]]; then
    if grep -qi centos /etc/os-release ; then
        yum install epel-release && yum install ShellCheck
    elif grep -qi fedora /etc/os-release ; then
        dnf install ShellCheck
    elif grep -qi ubuntu /etc/os-release ; then
        apt update && apt install shellcheck
    elif grep -qi debian /etc/os-release ; then
        apt update && apt install shellcheck
    else
        echo "Unknwon linux distro"
        exit 1
    fi
else
    echo "Unknown operating system"
    exit 1
fi
