#!/bin/bash

FILENAME=$1  #first parameter defines the filename (this is going to be the client id)

import -window root -resize 800x500! "${FILENAME}"


# the ! forces to resize non proportionally


