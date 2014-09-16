## overview

Procwatcher is simple process management tool for unix like system administrators.
There is no dependency except python 2.7!
Just install, and use it.

## usage

### install
```bash
python setup.py install
```

### config file (ini style)

```bash
# cat /etc/procwatcher.conf
[someprocess1]
path=/path/to/executable1

[someprocess2]
path=/path/to/executable2
```

### daemon

daemonize $INSTALL_PATH/procwatcherd

### command

```bash
$INSTALL_PATH/pwctl status
$INSTALL_PATH/pwctl start somprocess1
$INSTALL_PATH/pwctl stop somprocess2 # send quit(3) signal
$INSTALL_PATH/pwctl restart somprocess1
$INSTALL_PATH/pwctl alarm somprocess1 # send alarm(14) signal
```
