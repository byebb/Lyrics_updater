# -- coding: utf-8 --
# -*- coding: utf-8 -*-

import sys
import time
import parseConfigFiles as Config
import parseTextFiles as text
import generateOutput as output
import generateOutput7 as output7
import os, codecs, io
import glob
import unicodedata
import traceback
import json

import argparse

# Check if interaction is needed
parser = argparse.ArgumentParser(description='By default the interactive File Selector is opened for creation of single files...')   
parser.add_argument("-t", "--type", help="Default: Interactive", default="interactive")
parser.add_argument("-l", "--limit", help="Default: ALL", default="0")
parser.add_argument("-s", "--style", help="Default: CONSOLE", default="CONSOLE")
parser.add_argument("-n", "--song", help="Default: NONE", default="none")
args = parser.parse_args()

print_style="CONSOLE"
if args.style is not "CONSOLE":
    print_style="WEBSITE"


def PrintC(style, content):
    if (style is "CONSOLE"):
        print(content)
    else:
        print(content + "<br>")

# Create an empty dictionary to store all the parsed configuration data
configAll = {}
try:

    # Get the directory path for the folder containing the text files
    # loop over all files in master
    __file = __file__.decode(sys.getfilesystemencoding())
    dirname = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file)), os.pardir))
    folder = u"server_uploads"

    root = os.path.join(dirname, folder)   

    filename = ""

    if args.song is not "none":
        filename = args.song
                            
    songs_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file)), os.pardir))
    songs_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(songs_path)), os.pardir))
    songs_path = os.path.abspath(os.path.dirname(os.path.abspath(songs_path)))
        
    filename = str(root) + "/" + str(filename)

    base = os.path.basename(filename)
    base = base[:-4]

    # Parse all configuration files and add their data to configAll
    Config.ParseConfigFiles(configAll, print_style, base.replace(" ", "_"))

    PrintC(print_style, '============================================')
    PrintC(print_style, u'[START] CONVERTING SELECTED SONGS...')
    PrintC(print_style, u'[FOLDER] '+root+'...')
    PrintC(print_style, '============================================')

    # Start Library Creation Timer
    startLibraryTimer = time.time()

    completed_songs = []

    try:
        # Calculate performance of every song
        start_song_timer = time.time()

        # If filepath is not unicode, convert it to unicode using utf-8 encoding
        if not isinstance(filename, unicode):
            filename = unicode(filename, "utf-8")

        # Get the base name of the file
        filename = os.path.basename(filename)

        # If the file is a text file, generate output files for it
        if filename.endswith(".txt"):
            # print('-----------------------------')
            # print(u'[START] "{0}"'.format(filepath[:-4]))

            # Parse the text file and get its data
            inputText = text.ParseTextFile(root, filename, configAll["groupConfigs"])

            # Loop over each configuration and generate output files
            for Config in configAll["fileConfigs"]:
                output.CreateOutputs(Config, configAll["groupConfigs"], inputText)

            # Loop over each configuration from pro7 and generate output files
            for Config in configAll["fileConfigs7"]:
                output7.CreateOutputs(Config, configAll["groupConfigs7"], inputText)

            executionTime = (time.time() - start_song_timer)
            PrintC(print_style, u'[RUNTIME] [ {1} sec ] \t [ {0} ]'.format(filename[:-4], str(round(executionTime, 2))))           

    # If an error occurs, print the error message
    # except ValueError as err:
        # PrintC(print_style, err)
    except:
        traceback.print_exc()

    executionTime = (time.time() - startLibraryTimer)
    PrintC(print_style, '============================================')
    PrintC(print_style, u'[TOTAL RUNTIME] {0} seconds (all selected files)'.format(str(round(executionTime, 1))))
    PrintC(print_style, "Generation Successful. This window can be closed")
    PrintC(print_style, '============================================')

# If an error occurs during configuration file parsing, print the error message
except ValueError as err:
    print("Exception occurred: check following text:")
    print(err)

