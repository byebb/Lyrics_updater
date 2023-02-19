# -- coding: utf-8 --

import sys
import os
import Tkinter
import tkFileDialog
from scripts.pp7_pb2 import presentation_pb2

__file = __file__.decode(sys.getfilesystemencoding())
dirname = os.path.dirname(os.path.abspath(__file))
master = Tkinter.Tk()
filenames = tkFileDialog.askopenfilename(
    multiple=True, initialdir=dirname, title="Select Files to Read", filetypes=(("Pro7 files", "*.pro"),))
filenames = master.tk.splitlist(filenames)
for filepath in filenames:
    try:
        if not isinstance(filepath, unicode):
            filepath = unicode(filepath, "utf-8")
        filepath = os.path.basename(filepath)
        presentation = presentation_pb2.Presentation()
        f = open(filepath, "rb")
        presentation.ParseFromString(f.read())
        f.close()
        f = open(filepath + ".txt", "w")
        f.write(str(presentation))
        f.close()
    except ValueError as err:
        print(err)
