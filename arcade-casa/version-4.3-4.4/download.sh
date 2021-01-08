#!/usr/bin/env bash

if [ $# -eq 0 ]
then
  echo "usage: $0 <version>"
  exit 1
fi

VERSION=$1
FILE="casa-release-${VERSION}.tar.gz"
#URL=https://svn.cv.nrao.edu/casa/linux_distro/release/el6/$FILE
URL="https://casa.nrao.edu/download/distro/linux/release/el6/${FILE}"

# make sure we are in the source folder
HERE=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd $HERE

if [ ! -e "$FILE" ]; then
    curl -O  $URL
else
    echo "$FILE already downloaded."
fi
