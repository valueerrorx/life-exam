#!/bin/bash
# invokes the save dialog in libreoffice or (if already saved) just silently saves the doc

xdotool  search --name writer windowactivate && xdotool key ctrl+s
