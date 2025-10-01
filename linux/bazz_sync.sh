#!/bin/bash

set -e

URL="https://github.com/hhd-dev/kernel-bazzite/blob/bazzite-6.17/kernel-local?raw=true"

NAME="config-bazzite"

curl -L "$URL" -o "$NAME".new

if [ -e "$NAME" ]; then
    # Compare files and skip if identical
    if cmp -s "$NAME.new" "$NAME"; then
        echo "文件内容相同，无需更新。"
        rm "$NAME.new"
        exit 0
    fi

    diff -u "$NAME.new" "$NAME" | less

    read -p "是否应用更改？[Y/n] " REPLY
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        rm "$NAME.new"
    else
        mv "$NAME.new" "$NAME"
    fi
else
    mv "$NAME.new" "$NAME"
fi