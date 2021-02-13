import subprocess
import os

''' A Class for runing cmds with subprocess, also as a specific user '''
import pwd


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

        proc = subprocess.Popen(cmd,
                                shell=True,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                bufsize=0,
                                preexec_fn=None)
        for line in iter(proc.stderr.readline, b''):
            self._stderr += line.decode()

        for line in iter(proc.stdout.readline, b''):
            self._stdout += line.decode()
        proc.communicate()

    def runCmdasUser(self, cmd):
        ''' runs a command as student '''
        self._stderr = ""
        self._stdout = ""

        user_name = "student"
        uid = pwd.getpwnam(user_name).pw_uid
        guid = pwd.getpwnam(user_name).pw_gid

        proc = subprocess.Popen(cmd,
                                shell=True,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                bufsize=0,
                                preexec_fn=self.demote(user_name, uid, guid)
                                # env={'env_keep': ENV}
                                )
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
        return subprocess.check_output(cmd, preexec_fn=self.demote(1000, 1000))  # noqa

    def demote(self, user_name, user_uid, user_gid):
        """Pass the function 'set_ids' to preexec_fn, rather than just calling
        setuid and setgid. This will change the ids for that subprocess only"""
        def set_ids():
            try:
                # print("starting")
                # print ("uid, gid = %d, %d" % (os.getuid(), os.getgid()))
                # print (os.getgroups())
                # initgroups must be run before we lose the privilege to set it!
                os.initgroups(user_name, user_gid)
                # print("initgroups")
                os.setgid(user_gid)
                # this must be run last
                os.setuid(user_uid)
                # print("finished demotion")
                # print ("uid, gid = %d, %d" % (os.getuid(), os.getgid()))
                # print (os.getgroups())
            except Exception as error:
                print(error)
        return set_ids
