#!/bin/bash

latest_docs_commit=$(git log ./docs | head -1 | cut -d' ' -f 2)
code_dirs='platypush/plugins platypush/backend platypush/message/event'
target_dir='docs/source/platypush'

git diff --name-status $latest_docs_commit..HEAD $code_dirs \
        | grep '^A' | grep '\.py$' | awk '{print $2}' | while read filename; do

    module_name=$(echo -n $filename | sed -r -e 's/(.*)\.py$/\1/' | tr '/' '.')

    case $filename in
        platypush/backend/*)
            target_file="$target_dir/backend/$(echo -n $filename | sed -r -e 's/^platypush\/backend\/(.*)\.py$/\1.rst/' | tr '/' '.')"
            ;;
        platypush/plugins/*)
            target_file="$target_dir/plugins/$(echo -n $filename | sed -r -e 's/^platypush\/plugins\/(.*)\.py$/\1.rst/' | tr '/' '.')"
            ;;
        platypush/message/event/*)
            target_file="$target_dir/events/$(echo -n $filename | sed -r -e 's/^platypush\/message\/event\/(.*)\.py$/\1.rst/' | tr '/' '.')"
            ;;
    esac

    backticks='``'
    header_top="$backticks$module_name$backticks"
    echo "$header_top" > "$target_file"
    perl -e "print '=' x length('$header_top')" >> "$target_file"
    echo >> "$target_file"
    echo >> "$target_file"
    echo ".. automodule:: $module_name" >> "$target_file"
    echo -e "\t:members:" >> $target_file
    echo >> "$target_file"

    case $filename in
        platypush/backend/*)
            index_file="$target_dir/../backends.rst"
            header=$(cat $index_file | head -8)
            files=$(find docs/source/platypush/backend -type f -name '*.rst' | sort | sed -r -e 's/^docs\/source\/(.*)$/    \1/')
            echo $"$header" > $index_file
            echo $"$files" >> $index_file
            ;;
        platypush/plugins/*)
            index_file="$target_dir/../plugins.rst"
            header=$(cat $index_file | head -7)
            files=$(find docs/source/platypush/plugins -type f -name '*.rst' | sort | sed -r -e 's/^docs\/source\/(.*)$/    \1/')
            echo $"$header" > $index_file
            echo >> $index_file
            echo $"$files" >> $index_file
            ;;
        platypush/message/event/*)
            index_file="$target_dir/../events.rst"
            header=$(cat $index_file | head -7)
            files=$(find docs/source/platypush/events -type f -name '*.rst' | sort | sed -r -e 's/^docs\/source\/(.*)$/    \1/')
            echo $"$header" > $index_file
            echo >> $index_file
            echo $"$files" >> $index_file
            ;;
    esac
done

