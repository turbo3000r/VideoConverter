import os, shutil, sys, logging, subprocess, json, requests, time
from colorama import *

init()

logging.basicConfig(level=logging.DEBUG, filename="Logs\\Repair.log",filemode="a+",
                    format="[%(asctime)s] %(levelname)s: %(message)s")

with open("config.json") as f:
    config = json.load(f)
url = config["Update"]["check_url"]

def Info(msg):
    logging.info(msg)
    print(Fore.WHITE+Style.NORMAL+msg)

def Error(msg):
    logging.error(msg)
    print(Fore.RED+Style.NORMAL+msg)

def Critical(msg):
    logging.critical(msg)
    print(Fore.RED+Style.BRIGHT+msg)
    input("Press any key to exit")

def Repair_from_backup():
    Info("Repairing program from backup")
    Info("Repairing...")
    try:
        shutil.unpack_archive("backups\\backup.zip", extract_dir=os.getcwd())
        return True
    except:
        Error("Some error occurred during installing")
        logging.exception("Some error occurred during installing")
        return False

def Get_latest_version():
    Info("Try get latest version")
    for i in range(3):
        try:
            Info("Trying to connect to update server...")
            r = requests.get(url,timeout=0.5)
            if r.status_code == 200:
                Info("Success!")
                return r.json()["version"]
            else: 
                Error("Failed to get latest version")
                return ""
        except requests.exceptions.RequestException:
            Error(f"Connection failed. #{i} try")
    Error("Failed to reach server")
    return ""

def Install_latest_version():
    Info("Trying to install latest version")
    version = Get_latest_version()
    if len(version) == 0: return False
    else:
        Info("Starting Update.exe")
        
        DETACHED_PROCESS = 0x00000008
        subprocess.Popen(["Update.exe", f"{version}", "-backup"], creationflags=DETACHED_PROCESS, close_fds=True, shell=True)
        return True
    
if __name__ == "__main__":
    if len(os.listdir("backups\\")) <1: 
        Error("Missing backups. Repairing from backup unavailable")
        if not Install_latest_version(): Critical("Repair failed")
    else:    
        if Repair_from_backup():
            Info("Success!")
        else:
            Error("Repairing from backup failed")
            if not Install_latest_version(): Critical("Repair failed")
input("Press any key to exit")
             
        
