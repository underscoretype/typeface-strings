# built-in modules
import argparse, operator, codecs, os, ntpath, sys

# dependency modules
import clipboard

# local modules
import filehandler, text
from messages import error_messages, progress_messages


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

    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='textsample.txt', help='Input file in to extract possible strings from', type=str)
    parser.add_argument('font', metavar='font.ufo', help='Font file', type=str)
    parser.add_argument('-o', '--output', help='Name for the output file')
    parser.add_argument('-w', '--max-width', help='Desired maximumg word width', type=int)
    parser.add_argument('-m', '--min-width', help='Minimum word width', type=int)
    parser.add_argument('-r', '--results', help='Maximum number of result to be retrieved', type=int)
    parser.add_argument('-p', '--filter-punctuation', help='Remove any punctuation marks from the input', action='store_true')
    parser.add_argument('-n', '--filter-numbers', help='Remove any numbers from the input', action='store_true')
    parser.add_argument('-v', '--verbose', help='Print verbose processing information', action='store_true')
    parser.add_argument('-f', '--input-force', help='Limit the matches to words entirely made up of only these characters', type=lambda s: unicode(s, 'utf8'))
    parser.add_argument('-s', '--word-sequence', help='Allow combinations of several words from the source to match a given width -w', action='store_true')
    parser.add_argument('-c', '--letter-combinations', help='List of comma-separated n-grams that must be found in matched strings', type=str)
    parser.add_argument('-pb', '--pasteboard', help='Output results to the pasteboard, max 100 results', action='store_true')

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
    max_width = args.max_width
    min_width = args.min_width
    if max_width is not None and min_width is not None:
        if min_width >= max_width:
            exit(error_messages['min_max'])

    max_results = args.results
    verbose = args.verbose
    pasteboard = args.pasteboard
    sequence = args.word_sequence
    combinations = args.letter_combinations
    if combinations is not None:
        combinations = combinations.split(',')

    if sequence and not max_width:
        exit(error_messages['sequence_requires_width'])

    # check and load the input text file, or exit on failure
    inputText = filehandler.loadTextFile(input)    
    
    if args.filter_punctuation:
        inputText = text.removePunctuation(inputText)

    if args.filter_numbers:
        inputText = text.removeNumbers(inputText)

    force = []
    if args.input_force:
        force = args.input_force

    inputText = inputText.split()
    inputNumWords = len(inputText)

    # open the ufo font file with Robofab, or exit on failure
    font = filehandler.loadUfoFont(fontFile)
    
    # generate a list of all unicodes defined in the font
    glyphs = {}
    i = 0.0
    l = len(font) + 1
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

    # if we are not going to check for the lengths of word sequences we can
    # savely remove all duplicates (which also is not order preserving)
    if not sequence:
        inputText = text.removeDuplicates(inputText)

    inputNumUnique = len(inputText)


    i = 0.0
    l = len(inputText) + 1
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
    l = len(inputText) + 1
    s = 20

    results = []

    # calculate the combined advance widths of all possible separate words (no word sequences)
    if not sequence:
        wordWidths = text.getWordWidths(inputText, kerning, font, glyphs, max_width)
        i = i + 20
        progress(40 + (i / l * s), 100, progress_messages['widths'])

        results = [index for index, val in wordWidths]

        if combinations:
            results = text.filterByCombinations(results, combinations)
        
        i = i + 1
        progress(60 + (i / l * s), 100, progress_messages['matches'])

    else:
        # also consider words sequences for width calculations
        wordWidths = text.getWordAndSequenceWidths(inputText, kerning, font, glyphs, max_width, min_width)
        results = [index for index, val in wordWidths]

    if max_results is not None:
        results = results[0:max_results]


    if pasteboard:
        pb = ""
        for r in list(results)[:100]:
            pb += r.encode('utf-8') + "\n"
        clipboard.copy(pb)
    else:
        outputFile = codecs.open(output, "w", "utf8")
        outputFile.write("\n".join(results))


    progress(100, 100)

    if verbose:
        print('Font %(font)s contained %(glyphs)s glyphs' % { 'font': fontFile, 'glyphs': fontNumGlyphs })
        print('Input %(input)s contained %(words)d words (%(unique)d unique), of which %(valid)d were a match for the supplied font' %
              { 'input': input, 'words': inputNumWords, 'valid': inputNumValidWords, 'unique': inputNumUnique })
        if len(errorChars) > 0:
            print('For the supplied input, the following characters were missing from the font:')
            # when executed as binary, there is no stdout
            if sys.stderr.encoding is not None:
                (repr([x.encode(sys.stdout.encoding) for x in errorChars]).decode('string-escape'))
            else:
                print(errorChars)
        if max_width is not None:
            print('For supplied target width %(width)d the found results ranged from %(min)d to %(max)d' %
                  { 'width': max_width, 'min': minWordWidth, 'max': maxWordWidth })

    if pasteboard:
        print('%(matches)s matching words have been copied to your pasteboard. Done.' % { 'matches': min(len(results), 100) })
    else:
        print('%(matches)s matching words written to %(output)s. Done.' % { 'matches': len(results), 'output': output })