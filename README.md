# life-exam
A server/client application that allows to take over control of LiFE clients and provide a secure exam environment for schools.

This application is written in Python and PyQt.

## Prerequisites
Tools needed in order to provide 100% functionality are:
- xdotool
- imagemagick
- kde plasma > 5.12
- PyQt5
- Python 3
- [Twisted](https://pypi.org/project/Twisted/)
- and some others, see *setup.py*

## Install
- Run `sudo pip3 install .` in exam-life path, in order to global install missing modules
- check if you have Geogebra Web Apps inside `localhost/geogebra/`.  
  Be sure wich path points to your webserver root, see Configuration.  
  The entry html file is either `index.html` or `Geogebra.html`.
  ```
## Configuration
is made in *config/config.py*.  
Important things are shown here
```python
# Debugging Stuff, set Name of Client and a fix Pin Code
# set both empty, then we are NOT debugging
DEBUG_ID = "TestUser"
DEBUG_PIN = "1234"
# would you like to see Network Debugging Stuff?
DEBUG_SHOW_NETWORKTRAFFIC = True

# Web Server Root Directory
WEB_ROOT="/var/www/html/"
# Subdirectory to Geogebra
GEOGEBRA_PATH = "geogebra"

# sec, how often do we heartbeating
HEARTBEAT_INTERVALL = 5     
# sec, after what period we are starting heartbeating
HEARTBEAT_START_AFTER = 5   
# maximum number of Heartbeats missing, until a Client is marked as offline
MAX_HEARTBEAT_FAILS = 3     
# maximum number of Heartbeats missing, until a Client is removed
MAX_HEARTBEAT_KICK = 8      
```
Which Applications will be shown first when we create an Exam.  
What are your favorites?  
See *config/appranking.yml*
```yaml
apps:
   '1':
      - wxmaxima
      - geogebra
   '2':
      - libreOffice writer
      - libreOffice calc
   '3':
      - kate
      - kcalc
      - calligra words
      - musescore
      - audacity
```

## Running the Server and Client
`sudo python3 server/server.py`
runs the server.

`sudo python3 client/client.py`
runs the client.


if your setup can't find the twisted plugin add the follwing lines to your "sudoers" file
`sudo visudo`

```bash
Defaults    env_reset
Defaults    env_keep =  "PYTHONPATH DISPLAY"
Defaults    env_keep += "XAUTHORITY KDE_FULL_SESSION"
```

and PYTHONPATH to your */etc/environment*

```bash
PYTHONPATH="/home/student/.life/applications/life-exam"
```

![Image of life-exam](http://life-edu.eu/images/exam2.gif)
