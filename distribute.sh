#!/bin/bash

#zenity --info --text="Austeilen beginnt …" --width=250

zenity --question --text="Wollen Sie die Daten an die angeschlossenen Rechner verteilen?\n\nACHTUNG: Das Austeilen leert die entsprechenden Unterordner. Stellen Sie sicher, dass Sie eine KOPIE der Daten besitzen.\n\nDieser Vorgang kann eine Weile dauern. Sie werden benachrichtigt, wenn das Austeilen abgeschlossen ist." --width=250
ANSWER="$?"

if [ $ANSWER = "0" ]; then 
    
    i=1
    while [ $i -le 15 ]
    do
      if [ $i -le 9 ]; then
        d="0${i}"
      else
        d="${i}"
      fi
      ip="192.168.2.2${d}"
      directory="S${d}"
      
      echo "Sende den Inhalt des Verzeichnisses ~/Austeilen/${directory} an Gerät S${d} (IP: ${ip}) …"
      
      percentage=$(bc <<< "${i} * 100 / 15")
      #echo "$percentage"; echo "# Sende Daten an Rechner S${d} …" | zenity --progress --text "# Sende Daten an Rechner S${d} …" --percentage=0
      
      scp -r -P 32400 /home/lehrer/Schreibtisch/Austeilen/${directory}/* schueler@${ip}:/home/schueler/Schreibtisch/Austausch && rm -r /home/lehrer/Schreibtisch/Austeilen/${directory}/*
      
      i=$(( $i + 1 ))
    done
    
    #zenity --info --text="Austeilen abgeschlossen." --width=250
    notify-send -i /usr/share/icons/up -t 20000 "Austeilen abgeschlossen" "Das Austeilen wurde abgeschlossen."
    
    sleep 20
else
    notify-send -i /usr/share/icons/up "Austeilen abgebrochen."
fi

