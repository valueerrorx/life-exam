# life-exam-controlcenter 2
A simple server/client application that allows to take over control of LiFE clients and provide a secure exam environment for schools.

This application is written in Python, PyQt and Twisted.

Tools needed in order to provide 100% functionality are:
- xdotool
- imagemagick
- kde plasma > 5.12
- PyQt5
- python 3
- python twisted > 18.4.0 


![Image of life-exam](http://life-edu.eu/images/exam2.gif)

Run 
`sudo python3 setup.py`
in order to install the twisted plugin.


`sudo python3 server/server.py`
runs the server.

`sudo python3 client/client.py`
runs the client.


if your setup can't find the twisted plugin add the follwing lines to your "sudoers" file 
`sudo visudo`

>  Defaults    env_reset
>  Defaults    env_keep =  "PYTHONPATH DISPLAY"
>  Defaults    env_keep += "XAUTHORITY KDE_FULL_SESSION"

and PYTHONPATH to your /etc/environment

>   PYTHONPATH="/home/student/.life/applications/life-exam"

