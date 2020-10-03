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
- copy all files from DATA/EXAMCONFIG to ~/.life/EXAM/EXAMCONFIG
- place in your `~/.profile`
  ```bash 
  # is an old EXAM running > then stop it
  $HOME/.life/applications/life-exam/DATA/scripts/isEXAMafterReboot.sh
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

and PYTHONPATH to your /etc/environment

>   PYTHONPATH=".:/home/student/.life/applications/life-exam"

![Image of life-exam](http://life-edu.eu/images/exam2.gif)
