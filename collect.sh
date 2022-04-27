#!/bin/bash

zenity --question --text="Wollen Sie die Daten aller Rechner einsammeln?\n\nDieser Vorgang kann eine Weile dauern. Sie werden benachrichtigt, wenn das Einsammeln abgeschlossen ist." --width=250
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
      
      echo "Hole den Inhalt des Verzeichnisses ~/Austausch von Gerät S${d} (IP: ${ip}) …"
      
      percentage=$(bc <<< "${i} * 100 / 15")
      #echo "$percentage"; echo "# Hole Daten von Rechner S${d} …" | zenity --progress --text "# Hole Daten von Rechner S${d} …" --percentage=0
      
      scp -r -P 32400 schueler@${ip}:/home/schueler/Schreibtisch/Austausch/* "/home/lehrer/Schreibtisch/Eingesammelt/${directory}"
      
      i=$(( $i + 1 ))
    done

    #zenity --info --text="Alles eingesammelt." --width=250
    notify-send -i /usr/share/icons/down -t 20000 "Einsammeln abgeschlossen" "Das Einsammeln wurde abgeschlossen."
    sleep 20

else
    echo "Abbruch."
    #(
    #echo "25"; sleep 1
    #echo "# Statusmeldung 1"
    #echo "50"; sleep 1
    #echo "# Statusmeldung 2"
    #echo "100"
    #) | zenity --progress --text "Vorgang wird bearbeitet" --percentage=0
    notify-send -i /usr/share/icons/down "Einsammeln abgebrochen."
fi
