# -*- coding: utf-8 -*-
# Copyright 2012-2014 Narantech Inc.
#
# This program is a property of Narantech Inc. Any form of infringement is
# strictly prohibited. You may not, but not limited to, copy, steal, modify
# and/or redistribute without appropriate permissions under any circumstance.
#
#  __    _ _______ ______   _______ __    _ _______ _______ _______ __   __
# |  |  | |   _   |    _ | |   _   |  |  | |       |       |       |  | |  |
# |   |_| |  |_|  |   | || |  |_|  |   |_| |_     _|    ___|       |  |_|  |
# |       |       |   |_||_|       |       | |   | |   |___|       |       |
# |  _    |       |    __  |       |  _    | |   | |    ___|      _|       |
# | | |   |   _   |   |  | |   _   | | |   | |   | |   |___|     |_|   _   |
# |_|  |__|__| |__|___|  |_|__| |__|_|  |__| |___| |_______|_______|__| |__|

# default
import os
import atexit
import subprocess
import logging
import string
import random

# clique
import clique.runtime
import clique.web
from clique.web import endpoint


# current password.
PASSWD_FILE = clique.runtime.res_dir('_passwd')
# flag for sets the password from user.
PASSWD_FLAG = clique.runtime.res_dir('_haspasswd')


@endpoint()
def set_password(passwd, new_passwd):
  ret = _set_password(passwd, new_passwd)
  if ret:
    if not os.path.exists(PASSWD_FLAG):
      # create flag
      open(PASSWD_FLAG, 'w').close()
    # updates the contexts
    clique.web.cache('has_password', True)
    clique.web.cache('default_password', None)

  return ret


def _set_password(passwd, new_passwd):
  if passwd and os.path.exists(PASSWD_FILE):
    with open(PASSWD_FILE, 'r') as f:
      if passwd.strip() != f.read().strip():
        return False
  try:
    subprocess.check_call('(echo %s; echo %s) | sudo smbpasswd -a %s -s' % \
        (new_passwd, new_passwd, clique.runtime.app_name()), shell=True)
    subprocess.check_call('(echo %s; echo %s) | sudo passwd %s' % \
        (new_passwd, new_passwd, clique.runtime.app_name()), shell=True)
    with open(PASSWD_FILE, 'w') as f:
      f.write(new_passwd.strip())
    subprocess.check_call('sudo /etc/init.d/samba reload', shell=True)
    logging.info("Success set password.")
    return True
  except:
    logging.warn("Failed to set password.", exc_info=True)
    return False


def _gen_passwd():
  characters = string.digits
  return ''.join(random.choice(characters) for x in range(4))


def _check():
  """ Check old password file, due to the 3.6.140808 version to password
  file and flag were n the home folder.
  Next publish nfs, remove this function.
  """
  old_pw_file = clique.runtime.home_dir('_passwd')
  old_pw_flag = clique.runtime.home_dir('_haspasswd')

  if os.path.exists(old_pw_flag):
    cmd = 'mv {} {}'.format(old_pw_flag, PASSWD_FLAG)
    try:
      subprocess.check_call(cmd, shell=True)
    except:
      logging.warn("Failed to move old password flag.", exc_info=True)

  if os.path.exists(old_pw_file):
    cmd = 'mv {} {}'.format(old_pw_file, PASSWD_FILE)
    passwd = ''
    with open(old_pw_file, 'rb') as f:
      passwd = f.read()
      passwd = passwd.replace("\n", "")
      passwd.strip()

    try:
      subprocess.check_call(cmd, shell=True)
      if not passwd:
        passwd = _gen_passwd()
        cmd = 'sudo rm {}'.format(PASSWD_FLAG)
        subprocess.check_call(cmd, shell=True)

      subprocess.check_call('(echo %s; echo %s) | sudo smbpasswd -a %s -s' % \
          (passwd, passwd, clique.runtime.app_name()), shell=True)
      subprocess.check_call('(echo %s; echo %s) | sudo passwd %s' % \
          (passwd, passwd, clique.runtime.app_name()), shell=True)
      with open(PASSWD_FILE, 'w') as f:
        f.write(passwd.strip())
    except:
      logging.warn("Failed to move old password file.", exc_info=True)


def start():
  _check()
  subprocess.check_call('sudo /etc/init.d/samba start', shell=True)
  subprocess.check_call('sudo /etc/init.d/rpcbind start', shell=True)
  subprocess.check_call('sudo /etc/init.d/nfs-kernel-server start', shell=True)

  has_passwd = False
  default_passwd = None
  if not os.path.exists(PASSWD_FILE):
    # remove set password flag file
    if os.path.exists(PASSWD_FLAG):
      try:
        os.remove(PASSWD_FLAG)
      except:
        logging.warn("Failed to remove password flag file.")

    # generate new default password.
    default_passwd = _gen_passwd()
    logging.info("Setting password to a default value. %s", default_passwd)
    if not _set_password(None, default_passwd):
      logging.exception("Failed to create default password!");
  elif not os.path.exists(PASSWD_FLAG):
    # load default password.
    with open(PASSWD_FILE, 'r') as f:
      default_passwd = f.read().strip()
    clique.web.cache('default_password', default_passwd)
    logging.info("Loaded default password. %s", default_passwd)
  else:
    # has password and flag file(this mean password create by user).
    has_passwd = True
    logging.info("Detected has user password.")
  clique.web.cache('has_password', has_passwd)
  if default_passwd:
    clique.web.cache('default_password', default_passwd)

  clique.web.set_static_path(os.path.join(clique.runtime.res_dir(), "web"))
  logging.info("nfs service started.")


@atexit.register
def stop():
  logging.info("stopping the nfs service")
  subprocess.check_call('sudo /etc/init.d/nfs-kernel-server stop', shell=True)
  subprocess.check_call('sudo /etc/init.d/rpcbind stop', shell=True)
  subprocess.check_call('sudo /etc/init.d/samba stop', shell=True)


if __name__ == "__main__":
  start()
