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
- and some others, see _setup.py_

## Install

- Run `sudo pip3 install .` in exam-life path, in order to global install missing modules

## Configuration

is made in _config/config.py_.  
Important things are shown here

```python
# Debugging Stuff, set Name of Client and a fix Pin Code
# set both empty, then we are NOT debugging
DEBUG_ID = "TestUser"
DEBUG_PIN = "1234"
# would you like to see Network Debugging Stuff?
DEBUG_SHOW_NETWORKTRAFFIC = True

# Heartbeat Section
# be sure to enable in /DATA/scripts/exam-firewall.sh
HEARTBEAT_PORT = 43278
# Clients send Heartbeats in x sec
HEARTBEAT_INTERVALL = 4
# Server checks offline/online clients x sec
HEARTBEAT_CLEANUP = 2
# how long may a client be silent, after that it is marked as zombie x sec
MAX_HEARTBEAT_DELTA_TIME = 120
# how long may a client be silent until removed from Server
MAX_SILENT_TIME_OFf_CLIENT = 2 * MAX_HEARTBEAT_DELTA_TIME
```

### Which Applications will be shown first when we create an Exam.

What are your favorites?  
See _config/appranking.yml_

```yaml
apps:
  "1":
    - wxmaxima
    - geogebra
  "2":
    - libreOffice writer
    - libreOffice calc
  "3":
    - kate
    - kcalc
    - calligra words
    - musescore
    - audacity
```

### Be aware

Some important Starter Files are located at `./DATA/starter`.  
These Files will be overwrite local installed Starter Files with same Name!

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

and PYTHONPATH to your _/etc/environment_

```bash
PYTHONPATH="/home/student/.life/applications/life-exam"
```

![Image of life-exam](http://life-edu.eu/images/exam2.gif)
