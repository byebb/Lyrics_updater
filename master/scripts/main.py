# -- coding: utf-8 --
import sys
import parseConfigFiles as config
import parseTextFiles as text
import generateOutput as output
import generateOutput7 as output7
import os
import Tkinter
import tkFileDialog
import unicodedata

# Create an empty dictionary to store all the parsed configuration data
configAll = {}
try:
    # Parse all configuration files and add their data to configAll
    config.ParseConfigFiles(configAll)

    # Get the directory path for the folder containing the text files
    # loop over all files in master
    __file = __file__.decode(sys.getfilesystemencoding())
    dirname = os.path.dirname(os.path.abspath(__file))
    folder = u"..\\textFiles"
    root = os.path.join(dirname, folder)

    # Open a file dialog to select the text files to process
    master = Tkinter.Tk()
    filenames = tkFileDialog.askopenfilename(
        multiple=True, initialdir=root, title="Select Files to generate", filetypes=(("txt files", "*.txt"),))
    filenames = master.tk.splitlist(filenames)

    # Loop over each selected text file
    for filepath in filenames:
        try:
            # If filepath is not unicode, convert it to unicode using utf-8 encoding
            if not isinstance(filepath, unicode):
                filepath = unicode(filepath, "utf-8")

            # Get the base name of the file
            filepath = os.path.basename(filepath)

            # If the file is a text file, generate output files for it
            if filepath.endswith(".txt"):
                print(u'>>> Generating "{0}"'.format(
                    unicodedata.normalize("NFC", filepath).encode('ascii', 'ignore')))

                # Parse the text file and get its data
                inputText = text.ParseTextFile(
                    root, filepath, configAll["groupConfigs"])

                # Loop over each configuration and generate output files
                for config in configAll["fileConfigs"]:
                    output.CreateOutputs(
                        config, configAll["groupConfigs"], inputText)

                # Loop over each configuration from pro7 and generate output files
                for config in configAll["fileConfigs7"]:
                    output7.CreateOutputs(
                        config, configAll["groupConfigs7"], inputText)

        # If an error occurs, print the error message
        except ValueError as err:
            print(err)

    print("Generation Successful. This window can be closed")

# If an error occurs during configuration file parsing, print the error message
except ValueError as err:
    print("Exception occurred: check following text:")
    print(err)
