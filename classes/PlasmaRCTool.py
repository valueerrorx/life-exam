from configobj import ConfigObj
from config.config import PLASMACONFIG, USER_HOME_DIR, EXAM_DESKTOP_APPS
import logging
from pathlib import Path
import re
import os

"""
Some Infos
Config is organized based on "Containments" (e.g. [Containments][1]).
Each of those has a number to distinguish one from the other, and each one has different
blocks of options.
That's where "applets" come into play and each "Containment"
has its applets (usually one - [Containments][1][Applets][2])

[Containments][NumberOfContainment][Applets][NumberOf_Applet]
"""


class PlasmaRCTool():
    """ A Class for handling ~./.config/plasma-org.kde.plasma.desktop-appletsrc """

    _backup_launchers = None

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def saveOldLaunchers(self):
        """
        Search for old Launchers, that are Icons in Tasbar
        e.g.
        launchers = applications:org.kde.kate.desktop,applications:org.kde.kcalc.desktop,applications:GeoGebra Classic.desktop,applications:org.kde.calligrawords.desktop
        """
        plasma = ConfigObj(str(PLASMACONFIG), list_values=False, encoding='utf8')
        for item in plasma:
            try:
                section = plasma[item]
                launchers = section["launchers"]
                self._backup_launchers = launchers
                break
            except KeyError:
                continue

    def updatePlasmaConfig(self):
        """
        Update plasma Config with previously stored Data
        e.g.
        launchers = applications:org.kde.kate.desktop,applications:org.kde.kcalc.desktop,applications:GeoGebra Classic.desktop,applications:org.kde.calligrawords.desktop
        """
        plasma = ConfigObj(str(PLASMACONFIG), list_values=False, encoding='utf8')
        for item in plasma:
            try:
                section = plasma[item]
                launchers = section["launchers"]  # noqa

                if self._backup_launchers is not None:
                    # we do have a backup
                    section["launchers"] = self._backup_launchers
                    break
            except KeyError:
                continue

        # write new plasmaconfig
        plasma.write()

    def _extractFirstNumber(self, string):
        """ get first number of a String, or -1 if no number exists"""
        # getting numbers from string
        temp = re.findall(r'\d+', string)
        res = list(map(int, temp))
        number = -1
        try:
            number = res[0]
        except Exception:
            pass
        return number

    def _extractSecondNumber(self, string):
        """ get second number of a String, or -1 if no number exists"""
        # getting numbers from string
        temp = re.findall(r'\d+', string)
        res = list(map(int, temp))
        number = -1
        try:
            number = res[1]
        except Exception:
            pass
        return number

    def _getContainmentMaxNr(self):
        """Search for highest Number of Containments"""
        maxnr = -1
        plasma = ConfigObj(str(PLASMACONFIG), list_values=False, encoding='utf8')
        for item in plasma:
            if item.find('Containments]') != -1:
                nrr = self._extractFirstNumber(item)
                # first nr ist containmentNr
                if nrr > maxnr:
                    maxnr = nrr
        return maxnr + 1

    def _getAppletsMaxNr(self, con):
        """Search for highest Number of Applets inside specific Containments"""
        maxnr = -1
        plasma = ConfigObj(str(PLASMACONFIG), list_values=False, encoding='utf8')
        pattern = "Containments][%s][Applets]" % con
        for item in plasma:
            if item.find(pattern) != -1:
                nrr = self._extractSecondNumber(item)
                # first nr ist containmentNr
                if nrr > maxnr:
                    maxnr = nrr
        return maxnr + 1

    def _areThereStarters(self):
        """
        are there Starter Containments, search for ItemGeometriesHorizontal
        :returns: [True/False, ContainmentNr]
        """

        found = False
        Nr = -1
        plasma = ConfigObj(str(PLASMACONFIG), list_values=False, encoding='utf8')
        for item in plasma:
            try:
                section = plasma[item]
                geometry = section["ItemGeometriesHorizontal"]  # noqa

                Nr = self._extractFirstNumber(section.name)
                found = True
            except KeyError:
                continue
        return [found, Nr]

    def _ifLauncherExists(self, containerNr, path):
        """ test if this path exists allready """
        plasma = ConfigObj(str(PLASMACONFIG), list_values=False, encoding='utf8')
        pattern = "Containments][%s][Applets]" % containerNr
        found = False
        for item in plasma:
            if item.find(pattern) != -1:
                section = plasma[item]
                try:
                    url = section['url']
                    # is this our url
                    if path in url:
                        found = True
                        break
                except Exception:
                    pass
        return found

    def addApplet(self, config, containerNr, appletNr, appName):
        """ adds to the config File a Applet Section for this starter """

        rootDir = Path(__file__).parent.parent
        """ for example
        [Containments][37][Applets][29]
        immutability=1
        plugin=org.kde.plasma.icon
        """
        # does this starter exist?
        p1 = os.path.join(USER_HOME_DIR, ".local/share/plasma_icons/", appName)
        p2 = os.path.join(rootDir, "DATA/starter/", appName)

        if self._ifLauncherExists(containerNr, p2) is False:
            # starter does not exists
            app1 = 'Containments][%s][Applets][%s' % (containerNr, appletNr)
            config[app1] = {}
            config[app1]['immutability'] = 1
            config[app1]['plugin'] = "org.kde.plasma.icon"

            """ for example
            [Containments][37][Applets][29][Configuration]
            PreloadWeight=0
            localPath=/home/student/.local/share/plasma_icons/Exam Teacher.desktop
            url=file:////home/student/.life/applications/life-exam/DATA/starter/Exam Teacher.desktop
            """
            app1 = 'Containments][%s][Applets][%s][Configuration' % (containerNr, appletNr)
            config[app1] = {}
            config[app1] = {
                'PreloadWeight': 0,
                'localPath': p1,
                'url': p2
            }

    def addStarter(self):
        """ edit plasma-org.kde.plasma.desktop-appletsrc and add Desktop Starter """
        # search for e.g.
        # [Containments][37][Applets][28]
        # plugin=org.kde.plasma.icon

        # search for Containment Number
        maxContainmentNr = self._getContainmentMaxNr()
        starter = self._areThereStarters()

        # print("MAX Containment: %s" % maxContainmentNr)
        if starter[0]:
            # print("Starters are found at")
            # print("[Containments][%s][Applets]" % starter[1])
            maxAppletNr = self._getAppletsMaxNr(starter[1])
            # print("Applet MAX Nr = %s" % maxAppletNr)

        # geometry of the widgets
        left = 560
        top = 35
        space = 10
        # Update Config File
        config = ConfigObj(str(PLASMACONFIG), list_values=False, encoding='utf8')
        # there are no starter yet, create Container
        containerNr = starter[1]
        if starter[0] is False:
            con = 'Containments][%s' % (maxContainmentNr)
            config[con] = {}
            config[con] = {
                'ItemGeometriesHorizontal': "",
                'immutability': 1,
                'plugin': "org.kde.desktopcontainment",
                'formfactor': 0,
                'lastScreen': 0,
                'location': 0,
                'wallpaperplugin': "org.kde.image",
                'activityId': ""
            }

            containerNr = maxContainmentNr
            maxAppletNr = 1

        container = 'Containments][%s' % containerNr
        # append Widget like Applet-Nr:x,y,width,height,0;
        # we place 2 widgets on the desktop

        # create Apps list with som edata
        i = 0
        apps_list = []
        for _starter in EXAM_DESKTOP_APPS:
            if "stop.desktop".lower() in _starter.lower():
                apps_list.append([i, _starter, 80, 80])
            else:
                apps_list.append([i, _starter, 64, 96])
            i += 1

        geometry = ""
        for item in apps_list:
            geometry += "Applet-%s:%s,%s,%s,%s,0;" % (maxAppletNr + item[0], left + i * space, top, item[2], item[3])

        config[container]['ItemGeometriesHorizontal'] = geometry

        i = 0
        for item in apps_list:
            self.addApplet(config, containerNr, maxAppletNr + item[0], item[1])
            i += 1

        config.write()
