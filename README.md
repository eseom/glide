## overview

GLIDE is a simple process management tool for unix like system administrators.
There is no dependency except python 2.7. Just install and use it.

## usage

### install
```bash
python setup.py install
```

### config file (ini style)

```bash
# cat /etc/glide.conf
[process_name1]
path=/path/to/executable1

[process_name2]
path=/path/to/executable2
```

### daemon

daemonize $INSTALL_PATH/glided

### command

```bash
$INSTALL_PATH/glidectl status
$INSTALL_PATH/glidectl start process_name1
$INSTALL_PATH/glidectl stop process_name2 # send quit(3) signal
$INSTALL_PATH/glidectl restart process_name1
$INSTALL_PATH/glidectl alarm process_name2 # send alarm(14) signal
```
