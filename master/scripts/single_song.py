#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Standard library imports
import argparse
import codecs
import glob
import io
import json
import os
import sys
import time
import traceback
import unicodedata

# Third-party imports
# (none in this file)

# Local application imports
import generateOutput as output
import generateOutput7 as output7
import parseConfigFiles as Config
import parseTextFiles as text

def print_formatted(style, content):
    """Print content based on output style (console or website)"""
    if style == "CONSOLE":
        print(content)
    else:
        print(content + "<br>")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='By default the interactive File Selector is opened for creation of single files...')   
    parser.add_argument("-t", "--type", help="Default: Interactive", default="interactive")
    parser.add_argument("-l", "--limit", help="Default: ALL", default="0")
    parser.add_argument("-s", "--style", help="Default: CONSOLE", default="CONSOLE")
    parser.add_argument("-n", "--song", help="Default: NONE", default="none")
    args = parser.parse_args()

    print_style = "CONSOLE"
    if args.style != "CONSOLE":
        print_style = "WEBSITE"

    # Create an empty dictionary to store all the parsed configuration data
    config_all = {}
    try:
        # Get the directory path for the folder containing the text files
        # loop over all files in master
        __file_decoded = __file__.decode(sys.getfilesystemencoding())
        dirname = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file_decoded)), os.pardir))
        folder = u"server_uploads"

        root = os.path.join(dirname, folder)   

        filename = ""

        if args.song != "none":
            filename = args.song
                                
        songs_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file_decoded)), os.pardir))
        songs_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(songs_path)), os.pardir))
        songs_path = os.path.abspath(os.path.dirname(os.path.abspath(songs_path)))
            
        filename = str(root) + "/" + str(filename)

        base = os.path.basename(filename)
        base = base[:-4]

        # Parse all configuration files and add their data to config_all
        Config.ParseConfigFiles(config_all, print_style, base.replace(" ", "_"))

        print_formatted(print_style, '============================================')
        print_formatted(print_style, u'[START] CONVERTING SELECTED SONGS...')
        print_formatted(print_style, u'[FOLDER] '+root+'...')
        print_formatted(print_style, '============================================')

        # Start Library Creation Timer
        start_library_timer = time.time()

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
                # Parse the text file and get its data
                input_text = text.ParseTextFile(root, filename, config_all["groupConfigs"])

                # Loop over each configuration and generate output files
                for config in config_all["fileConfigs"]:
                    output.CreateOutputs(config, config_all["groupConfigs"], input_text)

                # Loop over each configuration from pro7 and generate output files
                for config in config_all["fileConfigs7"]:
                    output7.CreateOutputs(config, config_all["groupConfigs7"], input_text)

                execution_time = (time.time() - start_song_timer)
                print_formatted(print_style, u'[RUNTIME] [ {1} sec ] \t [ {0} ]'.format(filename[:-4], str(round(execution_time, 2))))           

        except Exception:
            traceback.print_exc()

        total_execution_time = (time.time() - start_library_timer)
        print_formatted(print_style, '============================================')
        print_formatted(print_style, u'[TOTAL RUNTIME] {0} seconds (all selected files)'.format(str(round(total_execution_time, 1))))
        print_formatted(print_style, "Generation Successful. This window can be closed")
        print_formatted(print_style, '============================================')

    # If an error occurs during configuration file parsing, print the error message
    except ValueError as err:
        print("Exception occurred: check following text:")
        print(err)

if __name__ == "__main__":
    main()

