import subprocess
import os
import psutil
from pathlib import Path


class closeNSaveApps():
    """
    a class to detect apps opend by the users.
    also trying to trigger autosave
    """
    def __init__(self):
        self.trigerdAutoSavedIDs = []
        self.allSaved = False
        self.saveMSG = "Bitte alle Dateien speichern und die laufenden Programme schließen!"

        USER = subprocess.check_output("logname", shell=True).rstrip().decode()
        self.USER_HOME_DIR = os.path.join("/home", str(USER))

    def killProcess(self, pid):
        """kill a running Process"""
        # maybe sudo kill -9 PID
        PID = int(pid)
        if psutil.pid_exists(PID):
            try:
                p = psutil.Process(PID)
                p.terminate()  # or p.kill()
                return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                print("PsUtils cant kill process %s ..." % PID)
                return False

    def _terminateApps(self, pids, app_id_list):
        """ kill all running Apps """
        try:
            for item in pids:
                app = item[0]
                app_id = item[1]
                # self.killProcess(app_id)
                print("Killing: %s %s" % (app, app_id))
            for item in app_id_list:
                self.killProcess(item)
        except Exception as e:
            print(e)
            print("Problem in _terminateApps() ...")

    def _fireSaveApps(self, pids, app_id_list):
        """
        NOT USED YET!!
        trigger dbus and xdotool to open apps
        :pids: PIDs from DBus
        :app_id_list: IDs from xdotool
        """
        for pid in pids:
            app = pid[0]
            app_id = pid[1]
            if app == "kate":
                savetrigger = "file_save_all"
            else:
                savetrigger = "file_save"
            try:
                prefix = "sudo -E -u student -H"
                qdbus_command = "%s qdbus org.kde.%s-%s /%s/MainWindow_1/actions/%s trigger" % (prefix, app, app_id, app, savetrigger)
                data = self.runAndWaittoFinish(qdbus_command)  # noqa
            except Exception as error:  # noqa
                print(error)

        # trigger Auto Save via xdotool but only ONE Time
        if(len(app_id_list) > 0):
            for application_id in app_id_list:  # try to invoke ctrl+s on the running apps
                if(self._isTriggered(application_id) is False):
                    command = "xdotool windowactivate %s && xdotool key ctrl+s &" % (application_id)
                    os.system(command)
                    print("ctrl+s sent to %s" % (application_id))

                    # remember this id
                    self.trigerdAutoSavedIDs.append(application_id)
                else:
                    print("ID %s allready in save State -waiting-" % application_id)

    def runAndWaittoFinish(self, cmd):
        """Runs a subprocess, and waits for it to finish"""
        stderr = ""
        stdout = ""
        proc = subprocess.Popen(cmd,
                                shell=True,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                )
        for line in iter(proc.stderr.readline, b''):
            stderr += line.decode()

        for line in iter(proc.stdout.readline, b''):
            stdout += line.decode()
        # Wait for process to terminate and set the return code attribute
        proc.communicate()
        return [proc.returncode, stderr, stdout]

    def clearDoubles(self, apps):
        """delete doubles, because they can be in global menu or local at the same time"""
        # using list comprehension to remove duplicated from list
        res = []
        [res.append(x) for x in apps if x not in res]  # noqa
        return res

    def addApplications(self, apps):
        """add everything from ~/.local/share/applications/ """
        path = "%s/.local/share/applications/" % self.USER_HOME_DIR
        for root, dirs, files in os.walk(path, topdown=False):  # noqa
            for name in files:
                apps.append(os.path.join(root, name))
        return apps

    def findUserProcesses(self):
        """ find all processes started by user """
        # alle Anwendungen
        # pgrep -l -u student
        process_list = []
        apps = subprocess.check_output("ps -eo comm,etime,user,tt | grep student", stderr=subprocess.DEVNULL, shell=True)
        apps = apps.decode()
        for line in apps.split('\n'):
            if line == "\n":
                continue
            chunks = line.split()
            if len(chunks) > 0:
                # only if not on TTY
                if chunks[-1] == "?":
                    # dont kill process sh
                    if chunks[0] != "sh":
                        if chunks[0] != "eclipse":
                            process_list.append(chunks[0])
        process_list = self.clearDoubles(process_list)
        return process_list

    def getThem(self, applist, processlist):
        """ compares running processes with installed apps, and creates a list """
        apps_list = []
        for app in applist:
            # only *.desktop files
            if ".desktop" in app.lower():
                app = app.replace(" ", "\ ").replace("(", "\(").replace(")", "\)")
                d = subprocess.check_output("cat %s | grep -i exec" % app, stderr=subprocess.DEVNULL, shell=True)
                response = d.decode()
            # just get the program name from Exec=<path>/name
            parts = response.split(" ")
            chunks = parts[0].split("=")
            chunks = chunks[1].split("/")
            app_name = chunks[-1]
                
            # Working
            if app_name != "":
                for p in processlist:
                    if p.lower() == app_name.lower():
                        # this is an running App
                        apps_list.append(p)
                        print(p)
                    
                        break
        return apps_list

    def findApps(self):
        """
        uses kbuildsycoca5 to list the current application menu from the system
        """
        apps = subprocess.check_output("kbuildsycoca5 --menutest", stderr=subprocess.DEVNULL, shell=True)
        apps = apps.decode()
        desktop_files_list = []

        for line in apps.split('\n'):
            if line == "\n":
                continue
            fields = [final.strip() for final in line.split('/')]

            filepath1 = Path("/usr/share/applications/%s" % fields[-1])
            filepath2 = Path("%s/.local/share/applications/%s" % (self.USER_HOME_DIR, fields[-1]))

            if filepath1.is_file():
                desktopfilelocation = filepath1

            elif filepath2.is_file():
                desktopfilelocation = filepath2
            else:
                desktopfilelocation = "none"

            if desktopfilelocation != "none":
                desktop_files_list.append(str(desktopfilelocation))

        # now we have pathes to desktop files, like /usr/share/applications/org.hydrogenmusic.Hydrogen.desktop
        # because in applications there are e.g. chrome apps we had to add them too, even they are not
        # listet in kbuildsycoca5
        desktop_files_list = self.addApplications(desktop_files_list)
        desktop_files_list = self.clearDoubles(desktop_files_list)
        return desktop_files_list

    def _countOpenApps(self):
        """ counts how much apps are open """
        open_apps = 0
        app_id_list = []
        finalPids = []

        applist = self.findApps()
        processlist = self.findUserProcesses()
        openApps = self.getThem(applist, processlist)
        openApps = self.clearDoubles(openApps)

        # these programs are qdbus enabled therefore we can trigger "save" directly from commandline
        found = False
        app = None

        for app in openApps:
            # DBus -------------------------------------
            command = "pidof %s" % (app)
            data = self.runAndWaittoFinish(command)
            # clean
            p = data[2].replace('\n', '')
            pids = p.split(' ')
            # check for empty data
            for item in pids:
                if(len(item) > 0):
                    finalPids.append([app, item])
                    open_apps += 1
                    found = True
                    # print("> %s" % app)

            # i dont find it on DBus
            if found is False:
                # xdotool -----------------------------------
                command = "xdotool search --name %s &" % (app)
                app_ids = subprocess.check_output(command, shell=True).decode().rstrip()
                if app_ids:
                    app_ids = app_ids.split('\n')
                    for app_id in app_ids:
                        app_id_list.append(app_id)
                    open_apps += 1
                    # print("xdo > %s" % app)
        return [open_apps, finalPids, app_id_list]

    def triggerAutosave(self):
        """
        this function uses xdotool to find windows and trigger ctrl + s shortcut on them
        which will show the save dialog the first time and silently save the document the next time
        """
        self.allSaved = False
        # clear Array
        del self.trigerdAutoSavedIDs[:]
        self.trigerdAutoSavedIDs = []

        # [open_apps, pids, app_ids]
        data = self._countOpenApps()
        self._terminateApps(data[1], data[2])


if __name__ == '__main__':
    closeApps = closeNSaveApps()
    closeApps.triggerAutosave()
