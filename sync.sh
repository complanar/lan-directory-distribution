#!/bin/bash

FETCH_PATH="/home/lehrer/Schreibtisch/Eingesammelt"
SHARE_PATH="/home/lehrer/Schreibtisch/Austeilen"
SHARE_ALL_PATH="$SHARE_PATH/Alle"
EXCHANGE_PATH="/home/schueler/Schreibtisch/Austausch"

DEVICES_FROM=1
DEVICES_TO=15

# Return $1 as string with two digits
get_two_digits () {
    if [ $1 -le 9 ]; then
        echo "0$1"
    else
        echo "$1"
    fi 
}

# Return local directory name for device $1
get_dir_name () {
    echo "S$( get_two_digits $1)"
}

# Return IP for device $1
get_ip () {
    echo "192.168.2.2$( get_two_digits $1)"
}

# ---------------------------------------------------------------------

# Share files with device $1
share_with () {
    IP=$( get_ip $1 )
    DIR=$( get_dir_name $1 )
    SRC="$SHARE_PATH/$DIR"
    # TODO: remove echo after testing :)
    echo "scp -r -P 32400 ${SRC}/* schueler@$IP:${EXCHANGE_PATH}/*"
    echo "rm -r ${SRC}/*"
}

# Fetch files from device $1
fetch_from () {
    IP=$( get_ip $1 )
    DIR=$( get_dir_name $1 )
    DST="SHARE_PATH/$DIR" 
    # TODO: remove echo after testing :)
    echo "scp -r -P 32400 schueler@$IP:${EXCHANGE_PATH}/* ${DST}/*"
}

# Copy files from $SHARE_ALL_PATH to individual local share directories
copy_to_all_shares () {
    for ((k=DEVICES_FROM;k<=DEVICES_TO;k++)); do
        DIR=$( get_dir_name $k )
        DST="$SHARE_PATH/$DIR"    
        # TODO: remove echo after testing :)
        echo "cp -r ${SHARE_ALL_PATH}/* ${DST}/*"
    done
}

# ---------------------------------------------------------------------

# Share with all devices
share () {
    for ((k=DEVICES_FROM;k<=DEVICES_TO;k++)); do
        share_with $k
    done
}

# Fetch from all devices
fetch () {
    for ((k=DEVICES_FROM;k<=DEVICES_TO;k++)); do
        fetch_from $k
    done
}

# ---------------------------------------------------------------------

if [ "$1" == "--share-each" ]; then
    share

elif [ "$1" == "--share-all" ]; then
    copy_to_all_shares
    share
    
elif [ "$1" == "--fetch" ]; then
    fetch

else
    cat USAGE.md
    echo ""
    echo "Hardcoded paths:"
    echo "----------------"
    echo "Local fetch base path : $FETCH_PATH"
    echo "Local share base path : $SHARE_PATH"
    echo "General share path    : $SHARE_ALL_PATH"
    echo "Remote exchange path  : $EXCHANGE_PATH"
    echo ""

fi
