#!/bin/bash

# ---------------------------------------------------------------------
# --- Paths and Constants ---------------------------------------------
# ---------------------------------------------------------------------

IP_TEMPLATE="192.168.2.2xx"
PORT=32400

DEVICES_FROM=1
DEVICES_TO=15

REMOTE_USER="schueler"
EXCHANGE_PATH="/home/${REMOTE_USER}/Schreibtisch/Austausch"

LOCAL_USER="lehrer"
FETCH_PATH="/home/${LOCAL_USER}/Schreibtisch/Eingesammelt"
SHARE_PATH="/home/${LOCAL_USER}/Schreibtisch/Austeilen"
SHARE_ALL_PATH="$SHARE_PATH/Alle"

# GLOBALS
# Calculate string lengths for IP_TEMPLATE substring replace
IP_PREFIX=${IP_TEMPLATE%%x*}
SUFFLEN=$(( ${#IP_TEMPLATE} - ${#IP_PREFIX} ))
JOBS=()

# ---------------------------------------------------------------------
# --- Utility Functions -----------------------------------------------
# ---------------------------------------------------------------------

# Return $1 as string with $2 digits
get_n_digits() {
    NUM=$1
    while [ ${#NUM} -lt $2 ]; do
        NUM="0${NUM}"
    done
    echo $NUM
}

# Return local directory name for device $1
get_dir_name () {
    echo "S$( get_n_digits $1 $SUFFLEN)"
}

# Return IP for device $1
get_ip() {
  echo "${IP_TEMPLATE%%x*}$(get_n_digits $1 $SUFFLEN)"
}

# Return SSH login for device $1
get_ssh_login () {
    echo "${REMOTE_USER}@$( get_ip $1 )"
}

# Copy files via SSH from $1 to $2
copy_via_ssh () {
    scp -r -P ${PORT} ${1}/* ${2}
}

# ---------------------------------------------------------------------
# --- Actual sharing/fetching -----------------------------------------
# ---------------------------------------------------------------------

# Share with devices (optional: from $1, else individual directory)
share () {
    # setup default directory (e.g. $SHARE_ALL_PATH)
    SRC=$1

    i=0
    JOBS=()
    for ((k=DEVICES_FROM;k<=DEVICES_TO;k++)); do
        LOGIN=$( get_ssh_login $k )
        DIR=$( get_dir_name $k )

        if [ -z "$1" ]; then
            # share from individual directory
            SRC="${SHARE_PATH}/${DIR}"
        fi
        DST="${LOGIN}:${EXCHANGE_PATH}"

        copy_via_ssh $SRC $DST &

        # Catch process ids in global variable
        JOBS[$i]=$!
        i=$((i + 1))

    done
}

# Fetch from all devices
fetch () {
    i=0
    JOBS=()
    for ((k=DEVICES_FROM;k<=DEVICES_TO;k++)); do
        LOGIN=$( get_ssh_login $k )
        DIR=$( get_dir_name $k )
        SRC="${LOGIN}:${EXCHANGE_PATH}"
        DST="${FETCH_PATH}/${DIR}"

        mkdir -p $DST

        copy_via_ssh $SRC $DST &

        # Catch process ids in global variable
        JOBS[$i]=$!
        i=$((i + 1))
    done
}

# Clear individual directories
clear_directories () {
    echo "Clear directories"
    for ((k=DEVICES_FROM;k<=DEVICES_TO;k++)); do
        SRC="${SHARE_PATH}/$( get_dir_name $k )"
        if [ -d "$SRC" ]; then
            if [ "$(ls -A $SRC)" ]; then
                rm -r ${SRC}/*
            fi
        fi
    done
}

# Create ZIP-file from fetched data
create_zip () {
    # create filename suggestion
    FILENAME=`date +"%Y-%m-%d_%H-%M-%S"`

    # query actual filename
    FILENAME=$( query_zip_name ${FILENAME} )
    if [[ "$FILENAME" != *.zip ]]; then
        FILENAME="${FILENAME}.zip"
    fi

    # create zip in a subshell to trim unnessacary parts of the paths
    (
        if [ -d ${FETCH_PATH} ]; then
            cd ${FETCH_PATH};
            zip -r "${FILENAME}" .
        else
            notify_error "Beim Erstellen der ZIP-Archivs ist ein Fehler aufgetreten.\n\nDer Ordner ${FETCH_PATH} konnte nicht gelesen werden."
        fi
    )
}

# ---------------------------------------------------------------------
# --- UI Utilities ----------------------------------------------------
# ---------------------------------------------------------------------

confirm_share_each () {
    QUESTION="Die Dateien in in\n\n    ${SHARE_PATH}/$( get_dir_name $DEVICES_FROM ) bis …/$( get_dir_name $DEVICES_TO )\n\nwerden ausgeteilt. Dies kann einen Moment dauern. Sie werden benachrichtigt, wenn das Austeilen abgeschlossen ist.\n\nWARNUNG: Die genannten Ausgabe-Ordner werden anschließend VOLLSTÄNDIG GELEERT. Stellen Sie sicher, dass Sie eine KOPIE der Daten besitzen.\n\nFortfahren?"
    zenity --question --title="Individuelles Austeilen" --text="$QUESTION" --width=500
    echo "$?"
}

confirm_share_all () {
    QUESTION="Die Dateien in\n\n    ${SHARE_ALL_PATH}\n\nwerden ausgeteilt.\n\n Dies kann einen Moment dauern. Sie werden benachrichtigt, wenn das Austeilen abgeschlossen ist."
    zenity --question --title="Einheitliches Austeilen" --text="$QUESTION" --width=500
    echo "$?"
}

confirm_fetch () {
    QUESTION="Die Dateien der Schüler werden eingesammelt und in\n\n    ${FETCH_PATH}/$( get_dir_name $DEVICES_FROM ) bis …/$( get_dir_name $DEVICES_TO )\n\nabgespeichert.\n\nDies kann einen Moment dauern. Sie werden benachrichtigt, wenn das Austeilen abgeschlossen ist."
    zenity --question --title="Einsammeln" --text="$QUESTION" --width=500
    echo "$?"
}

ask_to_zip () {
    QUESTION="Sollen die eingesammelten Dateien als ZIP-Archiv gespeichert werden?"
    zenity --question --title="ZIP-Datei erstellen" --width=500 --text="$QUESTION"
    echo "$?"
}

notify_success() {
    notify-send -i /usr/share/icons/$1 -t 20000 "Abgeschlossen" "Das $2 wurde abgeschlossen."
}

notify_abort () {
    notify-send -i /usr/share/icons/$1 "Abgebrochen" "Der Benutzer hat die Aktion abgebrochen"
}

notify_error() {
    notify-send -c "im.error" "Fehler" "$1"
}

query_zip_name () {
    zenity --file-selection --title="ZIP-Datei erstellen" --filename=$1 --save --confirm-overwrite --file-filter=*.zip
}

progess_bar () {
  RUNNING=${#JOBS[@]}
  (
    while [ $RUNNING -gt 0 ]; do
      RUNNING=0
      for PID in ${JOBS[@]}; do
          if kill -0 "$PID" > /dev/null 2>&1; then
            RUNNING=$(($RUNNING + 1))
          fi
      done

      JOBS_FINISHED=$((${#JOBS[@]} - $RUNNING))
      PERCENTAGE=$(bc <<< "$JOBS_FINISHED * 100 / ${#JOBS[@]}")
      echo "# ${JOBS_FINISHED}/${#JOBS[@]} abgeschlossen (${PERCENTAGE}%)."
      echo $PERCENTAGE

      sleep 0.5
    done
  ) | zenity --progress --title "${1}-Fortschritt" --text "Warte auf ${1} …" --percentage=0 --auto-close --width=500
}

# ---------------------------------------------------------------------
# --- Main Program ----------------------------------------------------
# ---------------------------------------------------------------------

if [ "$1" == "--share-each" ]; then
    ANSWER=$( confirm_share_each )

    if [ $ANSWER = "0" ]; then
        # UGLY: Working with global variables
        # Didn't find a way to return the PIDs from a subprocess without
        # breaking the multithreading
        share
        progess_bar "Upload"
        clear_directories
        notify_success "up" "individuelle Austeilen"
    else
        notify_abort "up"
    fi

elif [ "$1" == "--share-all" ]; then
    ANSWER=$( confirm_share_all )

    if [ $ANSWER = "0" ]; then
        # UGLY: Working with global variables
        # Didn't find a way to return the PIDs from a subprocess without
        # breaking the multithreading
        share "$SHARE_ALL_PATH"
        progess_bar "Upload"
        notify_success "up" "einheitliche Austeilen"
    else
        notify_abort "up"
    fi

elif [ "$1" == "--fetch" ]; then
    ANSWER=$( confirm_fetch )

    if [ $ANSWER = "0" ]; then
        # UGLY: Working with global variables
        # Didn't find a way to return the PIDs from a subprocess without
        # breaking the multithreading
        fetch
        progess_bar "Download"

        notify_success "down" "Einsammeln"

        # ask to zip
        ANSWER=$( ask_to_zip )

        if [ $ANSWER = "0" ]; then
            create_zip
        fi

    else
        notify_abort "down"
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
