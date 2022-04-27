#!/bin/bash

# ---------------------------------------------------------------------
# --- Paths and Constants ---------------------------------------------
# ---------------------------------------------------------------------

FETCH_PATH="/home/lehrer/Schreibtisch/Eingesammelt"
SHARE_PATH="/home/lehrer/Schreibtisch/Austeilen"
SHARE_ALL_PATH="$SHARE_PATH/Alle"
EXCHANGE_PATH="/home/schueler/Schreibtisch/Austausch"

DEVICES_FROM=1
DEVICES_TO=15

PORT=32400

# ---------------------------------------------------------------------
# --- Utility Functions -----------------------------------------------
# ---------------------------------------------------------------------

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
 
# Copy files via SSH from $1 to $2
copy_via_ssh () {
    # TODO: remove echo after testing
    echo "scp -r -P ${PORT} ${1}/* ${2}/*"
}

# ---------------------------------------------------------------------
# --- Actual sharing/fetching -----------------------------------------
# ---------------------------------------------------------------------

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
# --- UI Utilities ----------------------------------------------------
# ---------------------------------------------------------------------

confirm_share_each () {
    QUESTION="Die Dateien in in\n\n${SHARE_PATH}/$( get_dir_name $DEVICES_FROM )\nbis\n${SHARE_PATH}/$( get_dir_name $DEVICES_TO )\n\nwerden ausgeteilt. Dies kann einen Moment dauern. Sie werden benachrichtigt, wenn das Austeilen abgeschlossen ist.\n\nWARNUNG: Die genannten Ausgabe-Ordner werden anschließend VOLLSTÄNDIG GELEERT. Stellen Sie sicher, dass Sie eine KOPIE der Daten besitzen.\n\nFortfahren?"
    zenity --question --text="$QUESTION" --width=500
    echo "$?"
}

confirm_share_all () {
    QUESTION="Die Dateien in\n\n${SHARE_ALL_PATH}\n\nwerden ausgeteilt. Dies kann einen Moment dauern. Sie werden benachrichtigt, wenn das Austeilen abgeschlossen ist."
    zenity --question --text="$QUESTION" --width=500
    echo "$?"
}

confirm_fetch () {
    QUESTION="Die Dateien der Schüler werden eingesammelt und in\n\n${FETCH_PATH}/$( get_dir_name $DEVICES_FROM )\nbis\n${FETCH_PATH}/$( get_dir_name $DEVICES_TO )\n\n abgespeichert. Dies kann einen Moment dauern. Sie werden benachrichtigt, wenn das Austeilen abgeschlossen ist."
    zenity --question --text="$QUESTION" --width=500
    echo "$?"
}

notify_success() {
    notify-send -i /usr/share/icons/up -t 20000 "Abgeschlossen" "Das $1 wurde abgeschlossen."
}

notify_abort () {
    notify-send -i /usr/share/icons/up "Abgebrochen" "Der Benutzer hat die Aktion abgebrochen"
}

# ---------------------------------------------------------------------
# --- Main Program ----------------------------------------------------
# ---------------------------------------------------------------------

if [ "$1" == "--share-each" ]; then
    ANSWER=$( confirm_share_each )

    if [ $ANSWER = "0" ]; then 
        share
        notify_success "individuelle Austeilen"
    else
        notify_abort
    fi

elif [ "$1" == "--share-all" ]; then 
    ANSWER=$( confirm_share_all )

    if [ $ANSWER = "0" ]; then 
        share $SHARE_ALL_PATH
        notify_success "einheitliche Austeilen"
    else
        notify_abort
    fi
    
elif [ "$1" == "--fetch" ]; then 
    ANSWER=$( confirm_fetch )

    if [ $ANSWER = "0" ]; then
        fetch
        notify_success "Einsammeln"
    else
        notify_abort
    fi

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
