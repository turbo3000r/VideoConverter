import os, shutil, requests, logging, sys, json
from os.path import basename
from zipfile import ZipFile
from colorama import *

init(convert=True)

with open("config.json") as f:
    config = json.load(f)
url = config["Update"]["download_url"]

logging.basicConfig(level=logging.DEBUG, filename="Logs\\Update.log",filemode="a+",
                    format="[%(asctime)s] %(levelname)s: %(message)s")

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


def download_update(ver):
    Info(f"Start downloading update {ver}")
    for i in range(10):
        try:
            Info("Try to connect to update server...")
            r = requests.get(url=url, params=({"ver":ver}), timeout=0.5)
            if r.status_code == 200:
                Info("Success!")
                Info("Downloading update...")
                with open("update.zip", "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                Info("Update downloaded successfully!")
                return True
            elif r.status_code==404:
                Error(f"Requested version not found ({ver})")
                return False
            else:
                logging.debug(str(r.status_code))
                Error("Failed to download update")
                return False
        except requests.exceptions.RequestException:
            Error(f"Failed to connect to the update server. #{i} try")
    return False

def install_update():
    Info("Installing downloaded update")
    Info("Installing...")
    try:
        shutil.unpack_archive("update.zip", extract_dir=os.getcwd())
    except:
        logging.exception("Some error occurred during installing")
        return False
    Info("Removing downloaded update...")
    try:
        os.remove("update.zip")
    except:
        logging.exception("Some error occurred during removing")
        return False
    Info("Update installed successfully!")
    return True

def backup():
    try:
        with ZipFile('backups\\backup.zip', 'w') as zipObj:
        # Iterate over all the files in directory
            for folderName, subfolders, filenames in os.walk(os.getcwd()):
                for filename in filenames:
                    if ".git" in folderName or "backups" in folderName or "__pycache__" in folderName or "git" in filename or ".ini" in filename or "Update" in filename or "Builds" in folderName or "Repair" in filename: continue
                    #create complete filepath of file in directory
                    realfilePath = os.path.join(folderName, filename)
                    filePath = os.path.join(folderName.replace(os.getcwd(), ""), filename)
                    # Add file to zip
                    #logging.DEBUG(f"Store {filePath}")
                    zipObj.write(realfilePath, arcname=filePath)
    except:
        logging.exception("Backup failed")
        return False
    return True

#backup()
if __name__ == "__main__":
    args = sys.argv
    if download_update(args[1]):
        if args[2] == "-backup":
            Info("Making backup of current data")
            if backup():
                if install_update(): 
                    Info(f"Program was successfully updated to version {args[1]}")
                    input("Press any key to exit")
                else: Critical("Update have not been installed")     
            else:
                logging.exception("Some error occurred during backup")
                Critical("Failed to backup. Stop updating")
    else: Critical("Update have not been installed")
        
