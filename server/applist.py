 #! /usr/bin/env python3
# -*- coding: utf-8 -*-

from configobj import ConfigObj
import subprocess
from pathlib import Path
from config.config import *

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QSize


def findApps(applistwidget, appview):
    """
    uses kbuildsycoca5 to list the current application menu from the system
    """
    apps = subprocess.check_output("kbuildsycoca5 --menutest", stderr=subprocess.DEVNULL, shell=True)
    apps = apps.decode()
    desktop_files_list=[]
    
    
    for line in apps.split('\n'):
        if line == "\n":
            continue

        fields = [final.strip() for final in line.split('/')]
        
        filepath1 = Path("/usr/share/applications/%s" %fields[-1])
        filepath2 = Path("%s/.local/share/applications/%s" %(USER_HOME_DIR,fields[-1]))
    
        
        if filepath1.is_file():
            desktopfilelocation = filepath1
    
        elif filepath2.is_file():
            desktopfilelocation = filepath2
        else:
            desktopfilelocation = "none"
        
        if desktopfilelocation != "none":
            desktop_files_list.append(str(desktopfilelocation))
    
    listInstalledApplications(applistwidget, desktop_files_list, appview)





def listInstalledApplications(applistwidget, desktop_files_list, appview):
    """
    builds a final_applist that contains, desktopfilepath, filename, name, icon
    populates a QListWidgetItem with list entries
    """
    applist = []   # [[desktopfilepath,desktopfilename,appname,appicon],[desktopfilepath,desktopfilename,appname,appicon]]
        
        
    for desktop_filepath in desktop_files_list:
        desktop_filename = desktop_filepath.rpartition('/')
        desktop_filename = desktop_filename[2]
        
        thisapp = [desktop_filepath, desktop_filename, "", ""]
        file_lines = open(desktop_filepath, 'r').readlines() 
        
        if file_lines != "":
            for line in file_lines:
                if line == "\n":
                    continue
                elif line.startswith("Name="):   # this overwrites "Name" with the latest entry if it's defined twice in the .desktop file (like in libreoffice)
                    fields = [final.strip() for final in line.split('=')]
                    if thisapp[2] == "":   #only write this once
                        thisapp[2] = fields[1]
                elif line.startswith("Icon="):
                    fields = [final.strip() for final in line.split('=')]
                    thisapp[3] = fields[1]

        applist.append(thisapp)
                    
        
    #print(final_applist)
    
    #sort applist and put most used apps on top  
    final_applist = []
    for app in applist:
        if app[2] == "GeoGebra" or app[2] == "Kate" or app[2] == "GeoGebra Classic":
            final_applist.insert(0, app)
        elif app[2] == "KCalc"  or app[2] == "Calligra Words"  or app[2] == "LibreOffice Calc"  or app[2] == "LibreOffice Writer"  :
            final_applist.insert(1, app)
        elif app[2] == "Musescore"  or app[2] == "Audacity":
            final_applist.insert(2, app)
        else:
            final_applist.append(app)
            

    activated_apps = get_activated_apps()
        
    #clear appview first
    thislayout = appview.layout()
    while thislayout.count():
        child = thislayout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
        
    for APP in final_applist:   # most used app is on top of the list (listview is built from bottom therefore we reverse)
        #print(APP)
        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(QSize(40, 40));
        item.name = QtWidgets.QLabel()
        item.name.setText("%s" % APP[2])
        
        item.desktop_filename = APP[1]
        
        item.hint = QtWidgets.QLabel()
        item.hint.setText("sichbar")
        
        icon = QIcon.fromTheme(APP[3])
        item.icon = QtWidgets.QLabel()
        item.icon.setPixmap(QPixmap(icon.pixmap(28)))
        
        item.checkbox = QtWidgets.QCheckBox()
        item.checkbox.setStyleSheet("margin-right:-2px;")

        #turn on already activated apps  - add icons to appview widget in UI
        for activated_app in activated_apps:
            if activated_app in APP[1]:    
                item.checkbox.setChecked(True)
                iconwidget = QtWidgets.QLabel()
                iconwidget.setPixmap(QPixmap(item.icon.pixmap()))
                thislayout.addWidget(iconwidget)

        item.checkbox.clicked.connect(lambda: saveProfile(applistwidget, appview))
        
        verticalSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)

        grid = QtWidgets.QGridLayout()
        grid.addWidget(item.icon, 0, 0)
        grid.addWidget(item.name, 0, 1)
        grid.addItem(verticalSpacer, 0, 2)
        grid.addWidget(item.checkbox, 0, 3)
        grid.addWidget(item.hint, 0, 4)
                
        widget = QtWidgets.QWidget()
        widget.setLayout(grid)
        applistwidget.addItem(item) 
        applistwidget.setItemWidget(item, widget)
        



    


def saveProfile(applistwidget, appview):
    """
    reads the contents of the listwidget, searches for checked items
    reads the current plasmaconfig file
    changes the plasmaconfig
    writes the plasmaconfig file
    """
    
    #PLASMACONFIG=Path("plasma-org.kde.plasma.desktop-appletsrc")   # (this should be the config file that is then transferred to the clients and used for the exam desktop)
    
    if Path(PLASMACONFIG).is_file():
        config = ConfigObj(str(PLASMACONFIG))
        
        # find section for taskmanager (sections - because plasma could contain more than one taskmanager - just in case) 
        taskmanagersections = []
        for section in config:
            try:
                if config[section]["plugin"] == "org.kde.plasma.taskmanager":
                    taskmanagersections.append(section)  # don't save the actual section.. just the name of the section
            except:
                continue


    # get activated apps (those apps should be shown in taskmanager)
    items = []
    apps_activated = []
    for index in range(applistwidget.count()):
        items.append(applistwidget.item(index))
        
    #clear appview first
    thislayout = appview.layout()
    while thislayout.count():
        child = thislayout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
        
    #add checked items to apps_activated in order to save them to plasmaconf and make them visible in the UI
    for item in items:
        if item.checkbox.isChecked():
            
            icon = item.icon.pixmap()
            iconwidget = QtWidgets.QLabel()
            iconwidget.setPixmap(QPixmap(icon))
            
            apps_activated.append(item.desktop_filename)
            thislayout.addWidget(iconwidget)
            
 
            
            
            
            
            
        
    #generate appstring (value for the launchers section of the taskmanager applet)
    appstring = ""


    #prepare config section for the taskmanager applet
    for targetsection in taskmanagersections:
        launchers_section = "%s][Configuration][General" %(targetsection)
        
        try:
            config[launchers_section]["launchers"] = []
        except KeyError:   #key does not exist..  no pinned applications yet
            config[launchers_section] = {}   
            config[launchers_section]["launchers"] = []  #create section(key)
            
        
        if len(apps_activated) > 0:
            for app in apps_activated:
                appstring="applications:%s" %(app)
                config[launchers_section]["launchers"].append(appstring)


    # write new plasmaconfig
    config.filename = str(PLASMACONFIG)
    config.write()



def get_activated_apps():
    """
    reads plasmaconfig file and searches for pinned apps in the taskmanager
    """
  
    if Path(PLASMACONFIG).is_file():
        config = ConfigObj(str(PLASMACONFIG))
        
        # find section for taskmanager (sections - because plasma could contain more than one taskmanager - just in case) 
        taskmanagersections = []
        for section in config:
            try:
                if config[section]["plugin"] == "org.kde.plasma.taskmanager":
                    taskmanagersections.append(section)  # don't save the actual section.. just the name of the section
            except:
                continue

    # get activated apps
    activated_apps = []
    for targetsection in taskmanagersections:
        launchers_section = "%s][Configuration][General" %(targetsection)
        
        try:
            activate_apps_string = config[launchers_section]["launchers"]
        except KeyError:   #key does not exist..  no pinned applications yet
            config[launchers_section] = {}   
            config[launchers_section]["launchers"] = []  #create section(key)
            
            appstring="applications:GeoGebra"    #add at least one application to activated apps
            config[launchers_section]["launchers"].append(appstring) #and prevent empty desktops
       
        for app in config[launchers_section]["launchers"]:
            app = app.split(":")
            #print(app[1])
            activated_apps.append(app[1])
       
        
            
            
    return activated_apps
    
