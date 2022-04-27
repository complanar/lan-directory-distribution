#!/bin/bash

#######################
###  CONFIGURATION  ###
#######################

PORT="32400"
IP_TEMPLATE="192.168.2.2xx"

IP_PREFIX=${IP_TEMPLATE%%x*}
PREFLEN=$(( ${#IP_TEMPLATE} - ${#IP_PREFIX} ))

TIMEOUT=5

REMOTE_USER="schueler"
REMOTE_DIR="/home/${REMOTE_USER}/Schreibtisch/Austausch"

LOCAL_USER="lehrer"
LOCAL_DIR="/home/${LOCAL_USER}/Schreibtisch/Eingesammelt"

FIRST_IP=1
LAST_IP=15

###################
###  FUNCTIONS  ###
###################

# $1 device number: integer
fetch_from() {
  IP=$(generate_ip $i)
  DEVICE=$(generate_host $i)

  echo "Hole Daten von Gerät ${DEVICE} (IP: ${IP}) …"
  scp -r -P $PORT ${REMOTE_USER}@${IP}:${REMOTE_DIR}/* ${LOCAL_DIR}/$DEVICE #&
  #pid=$!

  #sleep $TIMEOUT
  #kill $pid
  echo "    Von ${DEVICE} übertragen."
}

# $1 device number: integer
send_to() {
  IP=$(generate_ip $i)
  DEVICE=$(generate_host $i)

  echo "Sende Daten an Gerät ${DEVICE} (IP: ${IP}) …"
  scp -r -P $PORT ${LOCAL_DIR}/${DEVICE}/* ${REMOTE_USER}@${IP}:${REMOTE_DIR} && -rm -r ${LOCAL_DIR}/${DEVICE}/* #&
  #pid=$!

  #sleep $TIMEOUT
  #kill $pid
  echo "    An ${DEVICE} übertragen."
}

# $1 number: integer
# $1 desired number of digits: integer
number_digits() {
  number=$1
  while [ ${#number} -lt $2 ]; do
    number="0${number}"
  done
  echo $number
}

# $1 device number: integer
generate_ip() {
  echo "${IP_TEMPLATE%%x*}$(number_digits $1 $PREFLEN)"
}

# $1 device number: integer
generate_host() {
  echo "S$(number_digits $1 $PREFLEN)"
}

######################
###  MAIN PROGRAM  ###
######################

zenity --question --text="Wollen Sie die Daten aller Rechner einsammeln?\n\nDieser Vorgang kann eine Weile dauern. Sie werden benachrichtigt, wenn das Einsammeln abgeschlossen ist." --width=250
ANSWER="$?"

if [ $ANSWER = "0" ]; then

    JOBS_TOTAL=$(($LAST_IP - $FIRST_IP + 1))
    STARTED=0
    JOBS=()
    for i in $(seq $FIRST_IP $LAST_IP); do
      fetch_from $i &
      JOBS[$STARTED]="$!"
      STARTED=$((STARTED + 1))
    done

    RUNNING=$JOBS_TOTAL
    (
      while [ $RUNNING -gt 0 ]; do
        RUNNING=0
        for PID in ${JOBS[@]}; do
            if kill -0 "$PID" > /dev/null 2>&1; then
              RUNNING=$(($RUNNING + 1))
            fi
        done

        JOBS_FINISHED=$(($JOBS_TOTAL - $RUNNING))
        PERCENTAGE=$(bc <<< "$JOBS_FINISHED * 100 / $JOBS_TOTAL")
        echo "# ${JOBS_FINISHED}/${JOBS_TOTAL} abgeschlossen (${PERCENTAGE}%)."
        echo $PERCENTAGE

        sleep 1
        echo "STILL RUNNING: ${RUNNING}"
      done
    ) | zenity --progress --text "Warte auf Daten …" --percentage=0 --auto-close --width=500

    if [ "$?" = -1 ] ; then
      echo "Einsammeln abgebrochen."
      notify-send -i /usr/share/icons/down "Einsammeln abgebrochen."
    else
      notify-send -i /usr/share/icons/down -t 20000 "Einsammeln abgeschlossen" "Das Einsammeln wurde abgeschlossen."
    fi

else
    echo "Abbruch."
    notify-send -i /usr/share/icons/down "Einsammeln abgebrochen."
fi
