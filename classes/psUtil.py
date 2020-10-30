import psutil



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


    def GetProcessByName(self, name):
        """ search a Pid with Name Regex """
        processlist = []
        pids = psutil.pids()
        for pid in pids:
            try:
                p = psutil.Process(pid)
                if p.name == name:
                    processlist.append(p)
            except:
                pass
        return processlist 
