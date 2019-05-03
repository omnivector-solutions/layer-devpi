from pathlib import Path
from subprocess import check_call

from charmhelpers.core.hookenv import open_port
from charmhelpers.core.templating import render
from charmhelpers.core.host import adduser, chownr
from charms.reactive import when, when_not, set_flag

from charms.layer import status
from charms.layer.venv import ENV_BIN as DEVPI_ENV_BIN


DEVPI_PATH = Path('/usr/lib/devpi')


@when('venv.active')
@when_not('devpi.configured')
def configured_devpi():
    status.maintenance('Configuring devpi')

    DEVPI_PATH.mkdir(mode=0o755, parents=True, exist_ok=True)
    devpi_server_bin = DEVPI_ENV_BIN / 'devpi-server'

    # initialize devpi
    adduser('devpi')
    chownr(str(DEVPI_PATH), 'devpi', 'devpi', chowntopdir=True)
    check_call(['sudo', '-u', 'devpi', str(devpi_server_bin),
                '--init', '--serverdir', str(DEVPI_PATH)])

    # render service
    render('devpi.service', '/etc/systemd/system/devpi.service', context={
        'devpi_server_bin': devpi_server_bin,
        'devpi_path': str(DEVPI_PATH)
    })

    open_port(3141)

    # enable service
    check_call(['systemctl', 'enable', 'devpi.service'])

    # start service
    check_call(['systemctl', 'start', 'devpi.service'])

    status.active('devpi running')
    set_flag('devpi.configured')
