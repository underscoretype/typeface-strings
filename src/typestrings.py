
from robofab.world import RFont
import argparse, operator, codecs, os, ntpath, regex

def remove_punctuation(text):
    return regex.sub(ur"\p{P}+", "", text)

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


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='Input file to extract strings from', required=True)
    parser.add_argument('-f', '--font', help='Font file', required=True)
    parser.add_argument('-o', '--output', help='Name for the output file')
    parser.add_argument('-w', '--width', help='Desired word width', type=int)
    parser.add_argument('-m', '--max', help='Maximum words to be retrieved', type=int)
    parser.add_argument('-p', '--filter-punctuation', help='Remove any punctuation marks from the input', action='store_true')
    parser.add_argument('-v', '--verbose', help='Print verbose processing information', action='store_true')

    args = parser.parse_args()

    input = args.input
    fontFile = args.font

    if input is None or fontFile is None:
        exit("At least text input and font file need to be supplied. Exiting.")

    inputPath, inputExt = os.path.splitext(input)
    fontPath, fontExt = os.path.splitext(fontFile)

    # if no output file is provided, roll a default
    output = args.output
    if output is None:
        output = path_leaf(fontPath) + "_" + path_leaf(inputPath) + "_output.txt"

    # parse a target width if one was supplied
    width = None
    if args.width is not None:
        width = args.width

    # parse max results if a limiter was supplied
    max = None
    if args.max is not None:
        max = args.max

    verbose = args.verbose

    inputFile = open(input, 'r')
    inputText = inputFile.read().decode("utf8")

    if args.filter_punctuation:
        inputText = remove_punctuation(inputText)

    inputText = inputText.split()
    inputNumWords = len(inputText)

    # open the font file with Robofab
    font = loadUfoFont(fontFile)

    # generate a list of all unicodes defined in the font
    glyphs = {}
    for glyph in font:
        if glyph.unicode is not None:
            glyphs[glyph.unicode] = glyph.name

    fontNumGlyphs = len(glyphs)

    # filter the input text for words that can be written with the
    # available characters
    errorWords = []
    errorChars = []

    unicodes = glyphs.keys()
    for word in inputText:
        canWrite = True
        for letter in word:
            try:
                unicodes.index(ord(letter))
                continue
            except ValueError:
                errorWords.append(word)
                errorChars.append(letter)
                canWrite = False

    # remove words that have characters not present in the font file
    for error in set(errorWords):
        inputText.remove(error)

    inputNumValidWords = len(inputText)

    # extract kerning and apply kerning classes, if possible
    kerning = font.kerning
    if kerning is not None and font.groups is not None:
        kerning.explodeClasses(font.groups, font.groups)

    # calculate the combined advance widths of all possible words
    wordWidths = []
    for word in inputText:
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

    # remove all entries that are above width and limit to max, if supplied
    if width is not None and width > 0:
        for word, length in widthsAndWords:
            if length <= width:
                results.append(word)

            if len(results) >= max:
                break

        maxWordWidth = wordWidths[inputText.index(results[0])]
        minWordWidth = wordWidths[inputText.index(results[-1])]

    else:
        results = inputText
        if max is not None:
            results= results[0:max]

    outputFile = codecs.open(output, "w", "utf8")
    outputFile.write("\n".join(results))

    if verbose:
        print('Font %(font)s contained %(glyphs)s glyphs' % { 'font': fontFile, 'glyphs': fontNumGlyphs })
        print('Input %(input)s contained %(words)d words, of which %(valid)d were a match for the supplied font' %
              { 'input': input, 'words': inputNumWords, 'valid': inputNumValidWords })
        if width is not None:
            print('For supplied target width %(width)d the found results ranged from %(min)d to %(max)d' %
                  { 'width': width, 'min': minWordWidth, 'max': maxWordWidth})
    print('%(matches)s matching words written to %(output)s. Done.' % { 'matches': len(results), 'output': output})