import enum
import json
import os
import time
import tkinter as tk

import numpy as np
from pydash.objects import parse_int

# TODO: Enforce type dependency on inputs


def checkEmpty(item):
    print(item.get())


def openGUI(**kwargs):
    filename = "output.json"
    entries = []
    frames = []
    enumIDs = []
    enums = []
    window = tk.Tk()
    pad = 10

    topFrame = tk.Frame(window, relief=tk.RIDGE, borderwidth=1)
    topFrame.pack(side="top", fill=tk.X, expand=True)

    bottomFrame = tk.Frame(window)
    bottomFrame.pack(fill=tk.BOTH, expand=True)

    errorLabel = tk.Label(bottomFrame, text="There is an emtpy entry", fg="#f00")
    raceLabel = tk.Label(window, text="")
    raceLabel.pack(side="bottom")

    for index, (key, value) in enumerate(kwargs.items()):
        print("%s. %s = %s, (%s)" % (index, key, value, type(value)))
        frames.append(tk.Frame(topFrame))
        frames[index].pack(side="top", fill=tk.X, expand=True)
        tk.Label(frames[index], anchor="e", width=10, text=str(key)).pack(side="left")
        if isinstance(value, enum.Enum):
            enumIDs.append(index)
            entries.append(tk.IntVar(0))
            enumTemp = []
            for xindex, (enumType) in enumerate(type(value)):
                enumName = str(enumType.name)
                enumTemp.append(enumName)
                tk.Radiobutton(
                    frames[index], text=enumName, variable=entries[index], value=xindex
                ).pack(side="left", padx=5)
            enums.append(enumTemp)
        else:
            entries.append(tk.Entry(frames[index]))
            entries[index].pack(side="left", padx=pad, pady=pad, fill=tk.X, expand=True)

    def submitMeth():
        outList = []
        for i, (key, v) in enumerate(kwargs.items()):
            enumCount = 0
            if (entries[i].get() == "") or (
                (type(entries[i].get()) != type(v)) and (type(v) != enum.Enum)
            ):
                print(type(entries[i].get()), type(v))
                errorLabel.pack()
                return
            # else:
            errorLabel.pack_forget()
            print({"i": i, "idenum": enumIDs, "key": key}, np.isin(i, enumIDs))
            if np.isin(i, enumIDs):
                print(
                    {
                        "enums": enums,
                        str(key): enums[enumCount][parse_int(entries[i].get())],
                    }
                )
                outList.append(
                    {str(key): enums[enumCount][parse_int(entries[i].get())]}
                )
                enumCount += 1
            else:
                outList.append({str(key): entries[i].get()})
        print(outList)
        with open(filename, "w") as outfile:
            json.dump({"data": outList}, outfile, indent=4, sort_keys=True)
        try:
            os.system("notepad.exe {}".format(filename))
            time.sleep(2)
            window.destroy()
        except:
            tk.messagebox.showerror(title="Error", message="File failed to generate")

    def clearMeth():
        errorLabel.pack_forget()
        for entry in entries:
            entry.delete(0, tk.END)

    tk.Button(bottomFrame, text="Submit Values", command=submitMeth).pack(side="left")
    tk.Button(bottomFrame, text="Clear Inputs", command=clearMeth).pack(side="right")

    window.mainloop()
