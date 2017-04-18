import os
from robofab.world import RFont

from messages import error_messages

def loadUfoFont(fontFile):
    if not file_exists(fontFile):
        exit(error_messages['font_not_found'] + ' Supplied: ' + fontFile)
    else:
        return RFont(fontFile)

def loadTextFile(textFile):
    if not file_exists(textFile):
        return exit(error_messages['textfile_not_found'] + ' Supplied: ' + textFile)
    else:
        inputFile = open(textFile, 'r')
        inputText = inputFile.read().decode("utf8")
        return inputText

def file_exists(file_path):
    if not file_path:
        return False
    else:
        # essentially UFO's are folders, but check file or folder to be sure
        return os.path.isfile(file_path) or os.path.isdir(file_path)