import psutil


class PsUtil():
    """ Library for psutil """

    def closePID(self, pid):
        """kill the old running Process"""
        PID = int(pid)
        if psutil.pid_exists(PID):
            try:
                p = psutil.Process(PID)
                p.terminate()  # or p.kill()
                return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                print("PsUtils cant kill process %s ..." % PID)
                return False

    def _searchInArray(self, arr, pattern):
        """ Search within Array """
        found = False
        for item in arr:
            if pattern.lower() in item.lower():
                found = True
                break
        return found

    def GetProcessByName(self, name, cmdline=None):
        """
        search for a process with Name Regex
        :name: the name of the process
        :cmdline: arguments in them command line for this process
        """
        processlist = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if name.lower() in proc.name().lower():
                    if cmdline is not None:
                        cmdl = proc.cmdline()
                        if self._searchInArray(cmdl, cmdline):
                            data = ["%s" % proc.pid, "%s" % proc.name()]
                            processlist.append(data)
                    else:
                        data = ["%s" % proc.pid, "%s" % proc.name()]
                        processlist.append(data)
            except Exception as e:
                print(e)
        return processlist

    def killProcess(self, pid):
        """kill a running Process"""
        PID = int(pid)
        if psutil.pid_exists(PID):
            try:
                p = psutil.Process(PID)
                p.terminate()  # or p.kill()
                return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                print("PsUtils cant kill process %s ..." % PID)
                return False
