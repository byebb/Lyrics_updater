# -- coding: utf-8 --
import sys
import time
import parseConfigFiles as Config
import parseTextFiles as text
import generateOutput as output
import generateOutput7 as output7
import os
import Tkinter
import tkFileDialog
import glob
import unicodedata

import argparse


# Create an empty dictionary to store all the parsed configuration data
configAll = {}
try:
    # Parse all configuration files and add their data to configAll
    Config.ParseConfigFiles(configAll)

    # Get the directory path for the folder containing the text files
    # loop over all files in master
    __file = __file__.decode(sys.getfilesystemencoding())
    dirname = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file)), os.pardir))
    folder = u"textFiles"
    root = os.path.join(dirname, folder)
    
    # Check if interaction is needed
    parser = argparse.ArgumentParser(description='By default the interactive File Selector is opened for creation of single files...')
    parser.add_argument("-t", "--type", help="Default: Interactive", default="interactive")
    parser.add_argument("-l", "--limit", help="Default: ALL", default="0")
    args = parser.parse_args()
    filenames=[]

    if args.type == "all":
        filenames = glob.glob(root + u"\\*txt")
    else: 
        # Open a file dialog to select the text files to process
        master = Tkinter.Tk()
        filenames = tkFileDialog.askopenfilename(
            multiple=True, initialdir=root, title="Select Files to generate", filetypes=(("txt files", "*.txt"),))
        filenames = master.tk.splitlist(filenames)

    number_of_songs = 0
    if int(args.limit) > 0:
        number_of_songs = int(args.limit)

    print('============================================')
    print(u'[START] CONVERTING SELECTED SONGS...')
    print('============================================')

    # Start Library Creation Timer
    startLibraryTimer = time.time()

    counter = 0
    # Loop over each selected text file
    for filepath in filenames:
        counter += 1
        # print ('FILEPATH: ' + filepath)
        try:
            # Calculate performance of every song
            start_song_timer = time.time()

            # If filepath is not unicode, convert it to unicode using utf-8 encoding
            if not isinstance(filepath, unicode):
                filepath = unicode(filepath, "utf-8")

            # Get the base name of the file
            filepath = os.path.basename(filepath)

            # If the file is a text file, generate output files for it
            if filepath.endswith(".txt"):

                # print('-----------------------------')
                # print(u'[START] "{0}"'.format(filepath[:-4]))

                # Parse the text file and get its data
                inputText = text.ParseTextFile(
                    root, filepath, configAll["groupConfigs"])

                # Loop over each configuration and generate output files
                for Config in configAll["fileConfigs"]:
                    output.CreateOutputs(
                        Config, configAll["groupConfigs"], inputText)

                # Loop over each configuration from pro7 and generate output files
                for Config in configAll["fileConfigs7"]:
                    output7.CreateOutputs(
                        Config, configAll["groupConfigs7"], inputText)

                executionTime = (time.time() - start_song_timer)
                print(u'[RUNTIME] [ {1} sec ] \t [{2}] \t [ {0} ]'.format(filepath[:-4], str(round(executionTime, 2)), counter))

        # If an error occurs, print the error message
        except ValueError as err:
            print(err)

        if (number_of_songs > 0 and counter >= number_of_songs):
            break

    executionTime = (time.time() - startLibraryTimer)
    print('============================================')
    print(u'[TOTAL RUNTIME] {0} seconds (all selected files)'.format(str(round(executionTime, 1))))
    print("Generation Successful. This window can be closed")
    print('============================================')

# If an error occurs during configuration file parsing, print the error message
except ValueError as err:
    print("Exception occurred: check following text:")
    print(err)
