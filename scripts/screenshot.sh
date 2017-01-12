#!/bin/bash

NAME=$1  #first parameter defines the filename (this is going to be the client id)

import -window root -resize 160x100 "./FILESCLIENT/${NAME}.jpg"  


# the ! forces to resize non proportionally


