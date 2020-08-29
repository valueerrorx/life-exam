import subprocess
import os

''' A Class for runing cmds with subprocess, also as a specific user '''
class CmdRunner():
    def __init__(self):
        self._stderr = ""
        self._stdout = ""

    def getStderr(self):
        return self._stderr

    def getStdout(self):
        return self._stdout

    def getLines(self):
        ''' give me an array of lines from stdout '''
        # split the text
        words = self._stdout.split("\n")
        return words

    def runCmd(self, cmd):
        ''' runs a command '''
        self._stderr = ""
        self._stdout = ""

        proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0, preexec_fn=None)
        for line in iter(proc.stderr.readline, b''):
            self._stderr += line.decode()

        for line in iter(proc.stdout.readline, b''):
            self._stdout += line.decode()
        proc.communicate()

    def runCmdasUID(self, cmd, uid, guid):
        ''' runs a command as a specific User'''
        self._stderr = ""
        self._stdout = ""

        proc = subprocess.Popen(cmd,
                                shell=True,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                bufsize=0,
                                preexec_fn=self.demote(uid, guid))
        for line in iter(proc.stderr.readline, b''):
            self._stderr += line.decode()

        for line in iter(proc.stdout.readline, b''):
            self._stdout += line.decode()
        proc.communicate()

    def check_username(self):
        """Check who is running this script"""
        print(os.getuid())
        print(os.getgid())

    def check_id(self):
        """Run the command 'id' in a subprocess, return the result"""
        cmd = ['id']
        return subprocess.check_output(cmd)

    def check_id_as_user(self):
        """Run the command 'id' in a subprocess as user 1000,
        return the result"""
        cmd = ['id']
        return subprocess.check_output(cmd, preexec_fn=self.demote(1000, 1000))

    def demote(self, user_uid, user_gid):
        """Pass the function 'set_ids' to preexec_fn, rather than just calling
        setuid and setgid. This will change the ids for that subprocess only"""
        def set_ids():
            os.setgid(user_gid)
            os.setuid(user_uid)

        return set_ids
