#!/bin/bash

FETCH_PATH="/home/lehrer/Schreibtisch/Eingesammelt"
SHARE_PATH="/home/lehrer/Schreibtisch/Austeilen"
SHARE_ALL_PATH="$SHARE_PATH/Alle"
EXCHANGE_PATH="/home/schueler/Schreibtisch/Austausch"

DEVICES_FROM=1
DEVICES_TO=15

PORT=32400

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

# Return SSH login
get_ssh_login () {
    echo "schueler@$( get_ip $1 )"
}

# ---------------------------------------------------------------------

# Copy files via SSH from $1 to $2
copy_via_ssh () {
    # TODO: remove echo after testing
    echo "scp -r -P ${PORT} ${1}/* ${2}/*"
}

# Share with devices (optional: from $1, else individual directory)
share () {
    # setup default directory (e.g. $SHARE_ALL_PATH)
    SRC=$1
    
    for ((k=DEVICES_FROM;k<=DEVICES_TO;k++)); do
        LOGIN=$( get_ssh_login $k )
        DIR=$( get_dir_name $k )
        
        if [ -z "$1" ]; then
            # share from individual directory
            SRC="${SHARE_PATH}/${DIR}"
        fi
        
        DST="${LOGIN}:${EXCHANGE_PATH}"
        copy_via_ssh $SRC $DST 

        if [ -z "$1" ]; then
            # clear individual share directory+
            # TODO: remove echo after testing
            echo "rm -r ${SRC}"
        fi
    done
}

# Fetch from all devices
fetch () {
    for ((k=DEVICES_FROM;k<=DEVICES_TO;k++)); do
        LOGIN=$( get_ssh_login $k )
        DIR=$( get_dir_name $k )
        SRC="${LOGIN}:${EXCHANGE_PATH}"
        DST="${SHARE_PATH}/${DIR}"        
        copy_via_ssh $SRC $DST
    done
}

# ---------------------------------------------------------------------

if [ "$1" == "--share-each" ]; then
    share

elif [ "$1" == "--share-all" ]; then
    share $SHARE_ALL_PATH
    
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
