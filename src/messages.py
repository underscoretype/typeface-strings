
error_messages = {
    'input': '\nError: At least text input and font file need to be supplied. Exiting.',
    'min_max': '\nError: min-width can not be set to be greater than max-width. Exiting.',
    'font_not_found': '\nError: The supplied font could not be loaded. Make sure you are supplying a path to a .ufo file, including the .ufo extension. Exiting.',
    'textfile_not_found': '\nError: The supplied text file could not be loaded. Make sure you are supplying a path to a .txt file, including the .txt extension. Exiting.',
    'sequence_requires_width': '\nError: Flag to allow word sequences for matching without width -w. Please provide a width in conjunction with the sequence option. Exiting.'
}

progress_messages = {
    'start':    'Reading in files       ',
    'glyphs':   'Scanning UFO file      ',
    'words':    'Scanning for words     ',
    'widths':   'Calculating word widths',
    'matches':  'Finding matches        '
}