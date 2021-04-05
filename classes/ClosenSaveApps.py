# Autotrigger Save Part -------------------------------------------------------------------
    def _getArrayAsString(self, arr):
        string = ""
        for val in arr:
            string += val + " "
        return string

    def _isTriggered(self, application_id):
        """ is this ID allready autosav fired? """
        found = False
        for theid in self.trigerdAutoSavedIDs:
            if(theid == application_id):
                found = True
                break
        return found

    def _fireSaveApps(self, pids, app_id_list):
        """
        trigger dbus and xdotool to open apps
        :pids: PIDs from DBus
        :app_id_list: IDs from xdotool
        """
        for app in SAVEAPPS:
            if len(pids) > 0:
                if app == "kate":
                    savetrigger = "file_save_all"
                else:
                    savetrigger = "file_save"
                try:
                    print("dbus Pids: %s" % (self._getArrayAsString(pids)))
                    for pid in pids:
                        prefix = "sudo -E -u student -H"
                        qdbus_command = "%s qdbus org.kde.%s-%s /%s/MainWindow_1/actions/%s trigger" % (prefix, app, pid, app, savetrigger)
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

    def _countOpenApps(self):
        """ counts how much apps are open """
        open_apps = 0
        app_id_list = []
        finalPids = []
        for app in SAVEAPPS:
            # these programs are qdbus enabled therefore we can trigger "save" directly from commandline
            found = False
            # DBus -------------------------------------
            command = "pidof %s" % (app)
            data = self.runAndWaittoFinish(command)
            # clean
            p = data[2].replace('\n', '')
            pids = p.split(' ')
            # check for empty data
            for item in pids:
                if(len(item) > 0):
                    finalPids.append(item)
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

    def _stop_detectLoop(self):
        self.allSaved = True
        try:
            self.detectLoop.stop()
            # fire Event "We are ready to send the file"
            self._detectLoop_wait_thread.fireEvent_Done()
            self._detectLoop_wait_thread.stop()
            self._detectLoop_wait_thread = None
        except Exception:
            print("Error in _stop_detectLoop()")

    def _detectOpenApps(self, filename):
        """ counts the open Apps is called periodically by self.detectLoop """
        # [open_apps, pids, app_ids]
        data = self._countOpenApps()
        count = int(data[0])

        print("Offene Apps: %s" % count)
        self._fireSaveApps(data[1], data[2])

        # Fallback abort if user isn't closing apps
        fallback_time = 5 * 60  # 5 min

        # alle 10 sec repeat Message
        if self._detectLoop_wait_thread.getSeconds() % 10 == 0:
            self.inform(self.saveMSG, Notification_Type.Warning)

        if((count == 0) or (self._detectLoop_wait_thread.getSeconds() >= fallback_time)):
            self.allSaved = True
            self.detectLoop.stop()

            # fire Event "We are ready to send the file"
            self._detectLoop_wait_thread.fireEvent_Done()
            self._detectLoop_wait_thread.stop()
            self._detectLoop_wait_thread = None

            finalname = self.create_abgabe_zip(filename)
            self.client_to_server.setZipFileName(finalname)

    def triggerAutosave(self, filename, wait_thread):
        """
        this function uses xdotool to find windows and trigger ctrl + s shortcut on them
        which will show the save dialog the first time and silently save the document the next time
        """
        self.allSaved = False
        # clear Array
        del self.trigerdAutoSavedIDs[:]
        self.trigerdAutoSavedIDs = []
        """ some runtime errors, not now
        self.detectLoop = LoopingCall(lambda: self._detectOpenApps(filename))
        self.detectLoop.start(2)
        self.inform(self.saveMSG, Notification_Type.Warning)
        """

        self.inform("Abgabe ZIP wird an Lehrer versendet ...", Notification_Type.Warning)
        finalname = self.create_abgabe_zip(filename)
        self.client_to_server.setZipFileName(finalname)

        # fire event Zip is ready, Server will send back ExitExam now
        wait_thread.fireEvent_Done()
        wait_thread.stop()
