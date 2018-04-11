import subprocess
import traceback
import logging
#logger = logging.getLogger(__name__)
naviBaseSec = r'"C:\Program Files (x86)\EMC\Navisphere CLI\NaviSECCli.exe" -h {host} -user {user} -password {passwd} -scope 0 {command}'
#naviBaseSec = "/opt/Navisphere/bin/naviseccli -h {host} -user {user} -password {passwd} -scope 0 {command}"


def naviseccli(*args, **kwargs):
    """
    Runs the naviseccli command against the given IP.
    :param host: ip
    :param user: username
    :param passwd: password
    :param command: naviseccli command
    :returns:
        a tuple of (stdout, stderr)
    :raises Exception: bubbles up all exceptions
    """
    try:
        #logger.debug("NAVI-COMMAND: {}".format(naviBaseSec.format(**kwargs)))
        process = subprocess.Popen(
            naviBaseSec.format(**kwargs),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = process.communicate()
    except Exception:
        raise Exception(traceback.format_exc())
    return (out.decode(encoding='UTF-8'), err.decode(encoding='UTF-8'))