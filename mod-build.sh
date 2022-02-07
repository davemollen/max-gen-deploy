#!/bin/bash

cd $(dirname $0)

if [ ! -f gen_exported.cpp ] || [ ! -f gen_exported.h ]; then
  echo "Missing gen_exported.cpp/h files, please copy them to this folder"
  exit 1
fi

set -e

cd resources

###################################################################################################
# Give it a name or read CLI args

if [ "$1"x != ""x ]; then
  export NAME="$@"
else
  echo "Please type your plugin name, then press enter to confirm"
  read NAME
  if [ "${NAME}"x == ""x ]; then
    echo "Empty plugin name, cannot continue"
    exit 1
  fi
fi

###################################################################################################
# Copy files

rm -rf max-gen-plugin max-gen-plugin.tar.gz
mkdir max-gen-plugin
cp ../gen_exported.cpp ../gen_exported.h max-gen-plugin/
sed -e "s|@pluginame@|${NAME}|" max-gen-plugin.mk > max-gen-plugin/max-gen-plugin.mk

###################################################################################################
# Prepare tarball

COPYFILE_DISABLE=1 tar zhcf max-gen-plugin.tar.gz max-gen-plugin

###################################################################################################
# Request cloud build

python publish.py

###################################################################################################
# Cleanup

rm max-gen-plugin.tar.gz

###################################################################################################

cd $(dirname $0)
