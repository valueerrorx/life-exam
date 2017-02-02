#!/bin/bash
# invokes the save dialog in libreoffice or (if already saved) just silently saves the doc





# should take arguments in order to check for several appliciations at once and only raise reminder if none of the given apps is running otherwise try to invoke autosave
for APP in "$@"
do
   echo $APP
done
## durch all apps die als argument übergeben wurden durch gehen und prüfen ob sie gefunden werden...  falls gefunden in ein array legen und in folge für jeden eintrag im array ctrl+s bzw. was sonst so geht ausführen





APP1="writer"

WRITER=$(xdotool  search --name ${APP1} | wc -l)

if [[( ! $WRITER = "0" )]];then
    xdotool  search --name writer windowactivate && xdotool key ctrl+s
else
    kdialog  --msgbox "Bitte Speichern sie ihre Arbeit im Ordner ABGABE!" --title 'LIFE' --caption "LIFE" > /dev/null
    
fi


