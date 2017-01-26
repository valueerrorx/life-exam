#!/bin/bash

FILENAME=$1  #first parameter defines the filename (this is going to be the client id)


xdotool  search --name writer windowactivate && xdotool key ctrl+s
