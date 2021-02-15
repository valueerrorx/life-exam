from configobj import ConfigObj
from config.config import PLASMACONFIG
import logging
from pathlib import Path
import re

"""
Some Infos
Config is organized based on "Containments" (e.g. [Containments][1]). Each of those has a number to distinguish one from the other, and each one has different blocks of options. That's where "applets" come into play and each "Containment" has its applets (usually one - [Containments][1][Applets][2]) 
[Containments][NumberOfContainment][Applets][NumberOf_Applet]
"""


class PlasmaRCTool():
    """ A Class for handling ~./.config/plasma-org.kde.plasma.desktop-appletsrc """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def loadOldPlasmaConfig(self):
        """ the old plasma Config is loaded for backup"""
        if Path(PLASMACONFIG).is_file():
            try:
                return ConfigObj(str(PLASMACONFIG), list_values=False, encoding='utf8')
            except Exception as e:  # noqa
                self.logger.error(e)
        else:
            return None

    def updatePlasmaConfig(self, oldConfig):
        """
        Update plasma Config with previously stored Data
        e.g.
        [Containments][2][Applets][5][Configuration][General]
        launchers = applications:org.kde.kate.desktop,applications:org.kde.kcalc.desktop,applications:GeoGebra Classic.desktop,applications:org.kde.calligrawords.desktop
        we are searching fro launcher and place it in the same Containment
        """
        launchers = None
        if oldConfig is not None:
            for item in oldConfig.keys():
                if item.find('Configuration][General') != -1:
                    section = oldConfig[item]
                    try:
                        launchers = section["launchers"]
                    except KeyError:
                        continue

        if launchers is None:
            # Create new Config File
            config = ConfigObj(str(PLASMACONFIG), list_values=False, encoding='utf8')

            # read actual File
            plasma = ConfigObj(str(PLASMACONFIG), list_values=False, encoding='utf8')
            for item in plasma:
                if item.find('Configuration][General') != -1:
                    section = plasma[item]
                    try:
                        dummy = section["launchers"]
                        # here we are doing the Update
                        config[item] = plasma[item]
                        config[item]["launchers"] = launchers
                    except KeyError:
                        continue
                else:
                    # just copy top new Config
                    config[item] = plasma[item]
            # write new plasmaconfig
            config.write()

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
        are there Starter Containments, search for plugin=org.kde.plasma.icon
        :returns: [True/False, ContainmentNr]
        """

        found = False
        Nr = -1
        plasma = ConfigObj(str(PLASMACONFIG), list_values=False, encoding='utf8')
        for item in plasma:
            try:
                section = plasma[item]
                plugin = section["plugin"]
                if plugin in "org.kde.plasma.icon":
                    Nr = self._extractFirstNumber(section.name)
                    found = True
            except KeyError:
                continue
        return [found, Nr]

    def addStarter(self):
        """ edit plasma-org.kde.plasma.desktop-appletsrc and add Desktop Starter """
        # search for e.g.
        # [Containments][37][Applets][28]
        # plugin=org.kde.plasma.icon

        # search for Containment Number
        maxContainmentNr = self._getContainmentMaxNr()
        starter = self._areThereStarters()
        if starter[0]:
            maxAppletNr = self._getAppletsMaxNr(starter[1])
        print("MAX Containment: %s" % maxContainmentNr)
        print("Starters are found at")
        print("[Containments][%s][Applets]" % starter[1])
        print("Applet MAX Nr = %s" % maxAppletNr)
        # if starters found, than add the new ones to this Containment
        
        # else create new Containment
        
        k = 0
        
        # [Containments][NumberOfContainment][Applets][NumberOf_Applet]
        """
        [Containments][37][Applets][29]
immutability=1
plugin=org.kde.plasma.icon

[Containments][37][Applets][29][Configuration]
PreloadWeight=0
localPath=/home/student/.local/share/plasma_icons/Exam Teacher.desktop
url=file:///home/student/.local/share/applications/Exam Teacher.desktop
"""

        
