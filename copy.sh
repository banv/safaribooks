for dir in Books/*
do
    echo "$dir"
    mkdir -p "book2/$dir"
    for epub in "$dir/"*.epub
    do
        echo "$epub"
        cp -f "$epub" "book2/$dir/"
    done

    for mobi in "$dir/"*.mobi
    do
        echo "$mobi"
        cp -f "$mobi" "book2/$dir/"
    done


done

