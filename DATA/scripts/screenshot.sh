#!/bin/bash

FILENAME=$1  #first parameter defines the filename (this is going to be the client id)

import -window root -resize 160x100! "${FILENAME}"  


# the ! forces to resize non proportionally


