import yaml

''' A Class for handling config YAML File '''
import os
class ConfigTools():
    def __init__(self, path):
        self.path = path
        self.exists()
        self.yml = self.load_yml()
        
    def exists(self):
        """ Basic YAMl File exists? """
        if os.path.isfile(self.path) == False:
            print ("File not exist")
            data = dict(
                ui = dict(
                    exam_name = '',
                    delivery_intervall = '5',
                    screenshot_intervall = '20',
                    spellcheck_on = '1',
                    del_share_on_startup = '1',
                    del_share_on_shutdown = '0'
                )
            )
            with open(self.path, 'w') as file:
                yaml.dump(data, file, default_flow_style=False)
        
    def load_yml(self):
        """ Load the yaml file """
        with open(self.path, 'rt') as f:
            yml = yaml.safe_load(f.read())
        return yml
    
    def getYML(self):
        """ return the YAML struchture """
        return self.yml
    
    def getState(self, what):
        """ return the State of a CheckBox for String '1/0' """
        return what == '1'
        
    def setConfig(self, ui):
        """ set the Configuration """
        ui.examlabeledit1.setText(self.yml.get('ui').get('exam_name'))
        value = int(self.yml.get('ui').get('delivery_intervall'))
        ui.aintervall.setValue(value)
        value = int(self.yml.get('ui').get('screenshot_intervall'))
        ui.ssintervall.setValue(value)
        
        value = self.getState(self.yml.get('ui').get('spellcheck_on'))
        ui.spellcheck.setChecked(value)
        value = self.getState(self.yml.get('ui').get('del_share_on_startup'))
        ui.cleanabgabe.setChecked(value)
        value = self.getState(self.yml.get('ui').get('del_share_on_shutdown'))
        ui.exitcleanabgabe.setChecked(value)
        
    def addEntry(self, dictionary, sub, key, value):
        dictionary[sub][key] = value
        return dictionary
        
    def saveConfig(self, ui):
        """ save the Configuration of the UI """
        data = {}
        sub = "ui"
        data[sub] = {}
        data = self.addEntry(data, sub, "exam_name", ui.examlabeledit1.text())
        data = self.addEntry(data, sub, "delivery_intervall", "%s" % ui.aintervall.value())
        data = self.addEntry(data, sub, "screenshot_intervall", "%s" % ui.ssintervall.value())
        # -----------
        r = '0'
        if ui.spellcheck.isChecked():
            r = '1'
        data = self.addEntry(data, sub, "spellcheck_on", r)
        # -----------
        r = '0'    
        if ui.cleanabgabe.isChecked():
            r = '1'
        data = self.addEntry(data, sub, "del_share_on_startup", r)
        # -----------
        r = '0'
        if ui.exitcleanabgabe.isChecked():
            r = '1'
        data = self.addEntry(data, sub, "del_share_on_shutdown", r)
        
        with open(self.path, 'w') as file:
            yaml.dump(data, file, default_flow_style=False)
        
    