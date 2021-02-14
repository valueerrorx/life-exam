from configobj import ConfigObj
from config.config import PLASMACONFIG
import logging
from pathlib import Path


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
        """ Update plasma Config with previously stored Data"""
        # stored Apps are here
        """
        e.g.
        [Containments][2][Applets][5][Configuration][General]
        launchers = applications:org.kde.kate.desktop,applications:org.kde.kcalc.desktop,applications:GeoGebra Classic.desktop,applications:org.kde.calligrawords.desktop
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
