from tkinter import *
from tkinter.ttk import Combobox
from tkinter import filedialog as fd
import subprocess
from threading import Thread, Lock
import time
from functools import wraps

# save original function
__old_Popen = subprocess.Popen


# create wrapper to be called instead of original one
@wraps(__old_Popen)
def new_Popen(*args, startupinfo=None, **kwargs):
    if startupinfo is None:
        startupinfo = subprocess.STARTUPINFO()

    # way 1, as SO suggests:
    # create window
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    # and hide it immediately
    startupinfo.wShowWindow = subprocess.SW_HIDE

    # way 2, I cann't test it but you may try just:
    #startupinfo.dwFlags = subprocess.CREATE_NO_WINDOW

    return __old_Popen(*args, startupinfo=startupinfo, **kwargs)


# monkey-patch/replace Popen
subprocess.Popen = new_Popen

lock = Lock()
def Convert():
    global done
    p = subprocess.Popen(args=args, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    p.wait()
    lock.acquire()
    done = True
    lock.release()
    p.kill()

def check_status():
    Rb1["state"] = DISABLED
    Rb2["state"] = DISABLED
    Input["state"] = DISABLED
    profile["state"] = "disabled"
    Entr["state"] = DISABLED
    Save["state"] = DISABLED
    OutputDir["state"] = DISABLED
    global done
    done = False
    status = ["█▒▒▒▒▒▒▒▒▒","███▒▒▒▒▒▒▒","█████▒▒▒▒▒","███████▒▒▒","██████████"]
    l = Label(screen, text="Converting file\n Please wait.", font="Arial 14", width=12, justify='center')
    l.place(x=400, y=60)
    l2 = Label(screen, text=status[0], font="Arial 14", width=12, justify='center')
    l2.place(x=400, y=90)
    i = 0
    while True:
        lock.acquire()
        if done:
            lock.release()
            break
        lock.release()
        l2['text'] = status[i]
        i+=1
        if i >4:
            i=0
        screen.update()
        screen.update_idletasks()
        time.sleep(0.1)
    l.place_forget()
    l2.place_forget()
    Rb1["state"] = NORMAL
    Rb2["state"] = NORMAL
    Input["state"] = NORMAL
    profile["state"] = 'readonly'
    Entr["state"] = NORMAL
    Save["state"] = NORMAL
    OutputDir["state"] = NORMAL

def ConvertPrep():
    global args
    args = ["ffmpeg\\bin\\ffmpeg.exe",
        "-i", "", 
        "-c:v", "",
        "-preset", "",
        "-crf", "",
        ""
    ]
    args[2] = InpFile.replace("/","\\")
    args[4] = codec.get() 
    args[6] = profile.get()
    args[8] = Quality.get()
    args[9] = EndDir.replace("/","\\") + "\\"+Outfile.get()
    print(args)
    th = Thread(target=Convert, daemon=True)
    th.start()
    check_status()

def Open():
    global InpFile
    InpFile= fd.askopenfilename(filetypes=(
        ("Video Files", ("*.mp4", "*.mov", "*.mkv")),
        ("All Files", "*.*")
    ))
    print(InpFile)
#ffmpeg -i 1111.mp4 -c:v libx265 -preset fast -crf 17 output7.mp4
def OpenOutputDir():
    global EndDir
    EndDir= fd.askdirectory()
    print(EndDir)

def main():
    global codec, Quality, profile, tune, Outfile, screen, Save, Rb1, Rb2, Entr, profile, Input, OutputDir
    screen = Tk()
    screen.geometry("860x160")
    screen.title="Video Converter v:1.0"
    screen.iconbitmap("Vid.ico")
    Label(screen, text="Choose codec: ", font="Arial 14").grid(column=1, row=1, padx=5)
    codec = StringVar()
    Rb1 = Radiobutton(screen, text="H264", value="libx264", font="Arial 14", variable=codec, state=NORMAL)
    Rb2 = Radiobutton(screen, text="H264", value="libx265", font="Arial 14", variable=codec, state=NORMAL)
    Rb1.grid(column=1, row=2, padx=5)
    Rb2.grid(column=1, row=3, padx=5)
    Label(screen, text="Input quality{0-51}(0-lossless)\n 17-18 visual lossless: ", font="Arial 14").grid(column=2, row=1, rowspan=2, padx=5)
    Quality = StringVar()
    Entr = Entry(screen, width=10, textvariable=Quality, justify=CENTER, font="Arial 14")
    Entr.grid(column=2, row=3, padx=5)
    Label(screen, text="Speed(slower - better):", font="Arial 14").grid(column=3, row=1, rowspan=1, padx=5)
    profile = Combobox(screen, values=["ultrafast",
                                    "superfast",
                                    "veryfast",
                                    "faster",
                                    "fast",
                                    "medium",
                                    "slow",
                                    "slower",
                                    "veryslow"], width=14, justify= CENTER, state='readonly', font="Arial 14")
    profile.grid(column=3, row=2, rowspan=1, padx=5)
    Label(screen, text="Tune(film-best quality):", font="Arial 14").grid(column=4, row=1, rowspan=1, padx=5)
    tune = Combobox(screen, values=["film",
                                    "animation",
                                    "grain",
                                    "stillimage",
                                    "fastdecode",
                                    "zerolatency"], width=14, justify= CENTER, state='disabled', font="Arial 14")
    tune.grid(column=4, row=2, rowspan=1, padx=5, columnspan=2)
    Input = Button(screen, text="open video", command=Open, bg="gold", font="Arial 14")
    Input.grid(row=4,column=1, padx=5, pady=(10,0))
    OutputDir = Button(screen, text="open folder to save", bg="gold", command=OpenOutputDir, font="Arial 14")
    OutputDir.grid(row=4,column=2, columnspan=1, pady=(10,0))
    Outfile = StringVar()
    Out = Entry(screen, width=20, textvariable=Outfile, justify=CENTER, font="Arial 14")
    Out.grid(column=3, row=4, padx=5, columnspan=1, pady=(5,0))
    Out.insert(0, "output.mp4")
    Save = Button(screen, text="Convert", bg="green", font="Arial 14", command=ConvertPrep)
    Save.grid(row=4,column=4, columnspan=1, pady=(10,0))
    screen.mainloop()




main()