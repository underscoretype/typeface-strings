# built-in modules
import os, sys

# dependency modules
from defcon import Font

# local modules
from messages import error_messages


def loadUfoFont(fontFile):
    if not file_exists(fontFile):
        sys.exit(error_messages['font_not_found'] + ' Supplied: ' + fontFile)
    else:
        return Font(fontFile)

def loadTextFile(textFile):
    if not file_exists(textFile):
        sys.exit(error_messages['textfile_not_found'] + ' Supplied: ' + textFile)
    else:
        inputFile = open(textFile, 'r', encoding="utf8")
        inputText = inputFile.read()
        return inputText

def file_exists(file_path):
    if not file_path:
        return False
    else:
        # essentially UFO's are folders, but check file or folder to be sure
        return os.path.isfile(file_path) or os.path.isdir(file_path)