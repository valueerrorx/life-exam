CHECK_IPTABLES = "sudo iptables -L |grep DROP|wc -l"
EXEC_SCRIPT = "exec %s"
EXEC_STOP = "stop"
EXEC_START = "start"
EXEC_CONFIG = "config"

COPY = "cp -r %s %s"
CHOWN = "sudo chown -R %s:%s %s"

KILL_SERVER = "sudo pkill -f 'python server.py'"

START_TWISTD = "kdesudo 'twistd -l %s/client.log --pidfile %s/client.pid examclient -p %s -h %s -i %s'"
