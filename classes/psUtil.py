import psutil
from re import search


class PsUtil():
    ''' Library for psutil '''
    def _closePID(self, pid):
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
        """ RegEx serach within Array """
        found = False
        for item in arr:
            if search(pattern, item):
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
                if search(name, proc.name()):
                    if(cmdline is not None):
                        cmdl = proc.cmdline()
                        if self._searchInArray(cmdl, cmdline):
                            # print(cmdl)
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
