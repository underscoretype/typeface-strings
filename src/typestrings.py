import argparse, operator, codecs, os, ntpath, sys
import regex
from robofab.world import RFont


def remove_punctuation(text):
    return regex.sub(ur"\p{P}+", "", text)


def remove_numbers(text):
    return regex.sub(ur"\d+", "", text)


def getGlyphNameFromUnicode(unicode, glyphs):
    try:
        return glyphs[unicode]
    except KeyError:
        print("getGlyphNameFromUnicode KeyError for", unicode)
        return None


def loadUfoFont(fontFile):
    return RFont(fontFile)


# get file name part from path, from http://stackoverflow.com/a/8384788/999162
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


# progress bar, adapted from http://stackoverflow.com/a/27871113/999162
def progress(count, total, suffix=''):
    bar_len = 30
    filled_len = int(round(bar_len * count / float(total)))

    percents = int(round(100.0 * count / float(total), 0))
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ... %s\r' % (bar, percents, ' %', suffix))
    sys.stdout.flush()  # As suggested by Rom Ruben


if __name__ == '__main__':

    error_messages = {
        'input': 'Error: At least text input and font file need to be supplied. Exiting.',
        'min_max': 'Error: min-width can not be set to be greater than max-width. Exiting.'
    }

    progress_messages = {
        'start':    'Reading in files       ',
        'glyphs':   'Scanning UFO file      ',
        'words':    'Scanning for words     ',
        'widths':   'Calculating word widths',
        'matches':  'Iterating matches      '
    }

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='Input file to extract strings from', required=True)
    parser.add_argument('-f', '--font', help='Font file', required=True)
    parser.add_argument('-o', '--output', help='Name for the output file')
    parser.add_argument('-w', '--max-width', help='Desired word width', type=int)
    parser.add_argument('-m', '--min-width', help='Minimum word width', type=int)
    parser.add_argument('-r', '--results', help='Maximum words to be retrieved', type=int)
    parser.add_argument('-p', '--filter-punctuation', help='Remove any punctuation marks from the input', action='store_true')
    parser.add_argument('-n', '--filter-numbers', help='Remove any numbers from the input', action='store_true')
    parser.add_argument('-v', '--verbose', help='Print verbose processing information', action='store_true')
    parser.add_argument('-e', '--input-force', help='Limit the matches to words entirely made up of only these characters', type=lambda s: unicode(s, 'utf8'))

    args = parser.parse_args()

    i = 0
    l = 0
    s = 0

    input = args.input
    fontFile = args.font

    if input is None or fontFile is None:
        exit(error_messages['input'])

    progress(0, 100, progress_messages['start'])

    inputPath, inputExt = os.path.splitext(input)
    fontPath, fontExt = os.path.splitext(fontFile)

    # if no output file is provided, roll a default
    output = args.output
    if output is None:
        output = path_leaf(fontPath) + "_" + path_leaf(inputPath) + "_output.txt"

    # parse a target width if one was supplied
    max_width = None
    if args.max_width is not None:
        max_width = args.max_width

    min_width = None
    if args.min_width is not None:
        min_width = args.min_width

    if max_width is not None and min_width is not None:
        if min_width >= max_width:
            exit(error_messages['min_max'])


    # parse max results if a limiter was supplied
    max_results = None
    if args.results is not None:
        max_results = args.results

    verbose = args.verbose

    inputFile = open(input, 'r')
    inputText = inputFile.read().decode("utf8")

    if args.filter_punctuation:
        inputText = remove_punctuation(inputText)

    if args.filter_numbers:
        inputText = remove_numbers(inputText)

    force = []
    if args.input_force:
        force = args.input_force

    inputText = inputText.split()
    inputNumWords = len(inputText)

    # open the font file with Robofab
    font = loadUfoFont(fontFile)

    # generate a list of all unicodes defined in the font
    glyphs = {}
    i = 0.0
    l = len(font)
    s = 20
    for glyph in font:
        i = i + 1
        progress(0 + (i / l * s), 100, progress_messages['glyphs'])
        if glyph.unicode is not None:
            glyphs[glyph.unicode] = glyph.name

    fontNumGlyphs = len(glyphs)

    # filter the input text for words that can be written with the
    # available characters
    errorWords = []
    errorChars = []


    i = 0.0
    l = len(inputText)
    s = 20

    unicodes = glyphs.keys()
    for word in inputText:
        i = i + 1
        progress(20 + (i / l * s), 100, progress_messages['words'])
        for letter in word:
            if len(force) > 0 and letter not in force:
                if (word not in errorWords):
                    errorWords.append(word)

            try:
                unicodes.index(ord(letter))
                continue
            except ValueError:
                if (word not in errorWords):
                    errorWords.append(word)
                errorChars.append(letter)

    # remove words that have characters not present in the font file or passed in forced characters
    for error in set(errorWords):
        # remove ALL occurances of error in inputText
        inputText = [i for i in inputText if i != error]

    inputNumValidWords = len(inputText)

    # extract kerning and apply kerning classes, if possible
    kerning = font.kerning
    if kerning is not None and font.groups is not None:
        kerning.explodeClasses(font.groups, font.groups)

    i = 0.0
    l = len(inputText)
    s = 20

    # calculate the combined advance widths of all possible words
    wordWidths = []
    for word in inputText:
        i = i + 1
        progress(40 + (i / l * s), 100, progress_messages['widths'])

        lastLetter = None
        wordWidth = 0
        for letter in word:
            try:
                kernValue = kerning[(letter, lastLetter)]
                glyphName = getGlyphNameFromUnicode(ord(letter), glyphs)
                wordWidth += font[glyphName].width
                if kernValue is not None:
                    wordWidth += kernValue
                lastLetter = letter
            except KeyError:
                print("KeyError", word, glyphName, letter, ord(letter))
                continue

        wordWidths.append(wordWidth)

    # combine words as unique keys with their lengths
    combined = dict(zip(inputText, wordWidths))

    # sort by length, with words as dict values
    widthsAndWords = sorted(combined.items(), key=operator.itemgetter(1), reverse=True)

    results = []

    progress(50, 100)
    i = 0.0
    l = len(widthsAndWords)
    s = 40

    # remove all entries that are above width and limit to max, if supplied
    if max_width is not None:
        for word, length in widthsAndWords:
            i = i + 1
            progress(60 + (i / l * s), 100, progress_messages['matches'])

            if length <= max_width:
                if min_width is None and word not in results:
                    results.append(word)
                else:
                    if length > min_width and word not in results:
                        results.append(word)

            if max_results is not None and len(results) >= max_results:
                break

        if results and len(results) > 0:
            maxWordWidth = wordWidths[inputText.index(results[0])]
            minWordWidth = wordWidths[inputText.index(results[-1])]
        else:
            maxWordWidth = 0
            minWordWidth = 0

    else:
        results = set(inputText)
        if max_results is not None:
            results= results[0:max_results]

    outputFile = codecs.open(output, "w", "utf8")
    outputFile.write("\n".join(results))


    progress(100, 100)

    if verbose:
        print('Font %(font)s contained %(glyphs)s glyphs' % { 'font': fontFile, 'glyphs': fontNumGlyphs })
        print('Input %(input)s contained %(words)d words, of which %(valid)d (%(unique)d unique) were a match for the supplied font' %
              { 'input': input, 'words': inputNumWords, 'valid': inputNumValidWords, 'unique': len(results) })
        if len(errorChars) > 0:
            print('For the supplied input, the following characters were missing from the font:')
            print(repr([x.encode(sys.stdout.encoding) for x in errorChars]).decode('string-escape'))
        if max_width is not None:
            print('For supplied target width %(width)d the found results ranged from %(min)d to %(max)d' %
                  { 'width': max_width, 'min': minWordWidth, 'max': maxWordWidth})
    print('%(matches)s matching words written to %(output)s. Done.' % { 'matches': len(results), 'output': output})