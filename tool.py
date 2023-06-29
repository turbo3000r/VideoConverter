import subprocess
from functools import wraps

# save original function
__old_Popen = subprocess.Popen

# create wrapper to be called instead of original one
@wraps(__old_Popen)
def new_Popen(*args, startupinfo=None, **kwargs):
    if startupinfo is None:
        startupinfo = subprocess.STARTUPINFO()
    # create window
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    # and hide it immediately
    startupinfo.wShowWindow = subprocess.SW_HIDE

    return __old_Popen(*args, startupinfo=startupinfo, **kwargs)
