# built-in modules
import argparse, operator, codecs, os, ntpath, sys, logging

# dependency modules
import pyperclip as clipboard
from pymarkovchain import MarkovChain

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

    version = "0.2.0"

    parser = argparse.ArgumentParser()
    parser.add_argument('font', metavar='font.ufo', help='Font file', type=str)
    parser.add_argument('sample', metavar='textsample.txt', help='Input file in to extract possible strings from', type=str)
    parser.add_argument('-o', '--output', help='Name for the output file', type=str)
    parser.add_argument('-w', '--max-width', help='Desired maximumg word width', type=int)
    parser.add_argument('-m', '--min-width', help='Minimum word width', type=int)
    parser.add_argument('-r', '--results', help='Maximum number of result to be retrieved', type=int)
    parser.add_argument('-p', '--filter-punctuation', help='Remove any punctuation marks from the input', action='store_true')
    parser.add_argument('-n', '--filter-numbers', help='Remove any numbers from the input', action='store_true')
    parser.add_argument('-v', '--verbose', help='Print verbose processing information', action='store_true')
    parser.add_argument('-f', '--input-force', help='Limit the matches to words entirely made up of only these characters', type=str)
    parser.add_argument('-s', '--word-sequence', help='Allow combinations of several words from the source to match a given width -w', action='store_true')
    parser.add_argument('-c', '--letter-combinations', help='List of comma-separated n-grams that must be found in matched strings', type=str)
    parser.add_argument('-pb', '--pasteboard', help='Output results to the pasteboard, max 100 results', action='store_true')
    parser.add_argument('-g', '--generate', help='Use the input text to generate a randomized Markov chain based text from which to extract words (and word combinations), provide number of letters to generate. Especially useful in conjunction with -s. Ideally used with a sample text that contains punctuation, so sentences can be extracted for analysis', type=int)
    parser.add_argument('-sub', '--substitute', help='Pass in a text document with gylph name substitution rules, one per row', type=str)
    parser.add_argument('-uc', '--upper-case', help='Transform the input text to uppercase before calculations', action='store_true')
    parser.add_argument('-lc', '--lower-case', help='Transform the input text to lowercase before calculations', action='store_true')
    parser.add_argument('-tc', '--title-case', help='Transform the input text to titlecase before calculations', action='store_true')

    args = parser.parse_args()

    if args.verbose:
        print(("Type Strings script version: " + version))

    i = 0
    l = 0
    s = 0

    sample = args.sample
    fontFile = args.font

    if sample is None or fontFile is None:
        sys.exit(error_messages['input'])

    progress(0, 100, progress_messages['start'])

    inputPath, inputExt = os.path.splitext(sample)
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
            sys.exit(error_messages['min_max'])

    max_results = args.results
    verbose = args.verbose
    pasteboard = args.pasteboard
    sequence = args.word_sequence
    combinations = args.letter_combinations
    if combinations is not None:
        combinations = combinations.split(',')

    if sequence and not max_width:
        sys.exit(error_messages['sequence_requires_width'])

    # check and load the input text file, or exit on failure
    inputText = filehandler.loadTextFile(sample)    

    if args.upper_case:
        inputText = inputText.upper()

    if args.lower_case:
        inputText = inputText.lower()

    if args.title_case:
        inputText = inputText.title()
    
    # generate a markov chain based text from the input
    if args.generate and args.generate > 0:
        # disable error message about on-the-fly database
        logging.disable(logging.WARNING)
        mc = MarkovChain("./markov-chain-database")
        mc.generateDatabase(inputText)

        # reinstate logging
        logging.disable(logging.NOTSET)

        generatedText = ""
        while len(generatedText) < args.generate:
            if generatedText is not "":
                generatedText = generatedText + " "
            generatedText = generatedText + mc.generateString()
        inputText = generatedText

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

    substitution_rules = {}
    substitution_ignored = []
    if args.substitute:
        rules = filehandler.loadTextFile(args.substitute)
        for line in rules.split("\n"):
            # skip comments, empty lines, and obvisouly faulty rules
            if len(line) < 1 or line[:1] == "#" or line.find(":") == -1:
                continue

            parts = line.split(":")

            if parts[1] in font:
                substitution_rules[parts[0]] = parts[1]
            else:
                substitution_ignored.append(parts[1])
                
    

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

    unicodes = list(glyphs.keys())
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

    # Use kerning.find( (a, b) ) to get a kern value (with classes applied)
    kerning = font.kerning

    i = 0.0
    l = len(inputText) + 1
    s = 20

    results = []

    # calculate the combined advance widths of all possible separate words (no word sequences)
    if not sequence:
        wordWidths = text.getWordWidths(inputText, kerning, font, glyphs, substitution_rules, max_width)
        i = i + 20
        progress(40 + (i / l * s), 100, progress_messages['widths'])

        results = [index for index, val in wordWidths]

        if combinations:
            results = text.filterByCombinations(results, combinations)
        
        i = i + 1
        progress(60 + (i / l * s), 100, progress_messages['matches'])

    else:
        # also consider words sequences for width calculations
        wordWidths = text.getWordAndSequenceWidths(inputText, kerning, font, glyphs, substitution_rules, max_width, min_width)
        results = [index for index, val in wordWidths]

    if max_results is not None:
        results = results[0:max_results]

    if results:
        minWordWidth = text.getWordWidth(results[-1], kerning, font, glyphs, substitution_rules)
        maxWordWidth = text.getWordWidth(results[0], kerning, font, glyphs, substitution_rules)

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
        print(('Font %(font)s contained %(glyphs)s glyphs, %(unicodes)s with assigned unicodes' % { 'font': fontFile, 'glyphs': len(font), 'unicodes': fontNumGlyphs }))
        print(('Input %(input)s contained %(words)d words (%(unique)d unique), of which %(valid)d were a match for the supplied font %(font)s' %
              { 'input': args.sample, 'words': inputNumWords, 'valid': inputNumValidWords, 'unique': inputNumUnique, 'font': args.font }))

        if len(substitution_ignored) > 0:
            print('The following substitutions were ignored, because the inut font contained no such glyphs:')
            print(substitution_ignored)

        if len(errorChars) > 0:
            print('For the supplied input, the following characters were missing from the font:')
            # when executed as binary, there is no stdout
            if sys.stderr.encoding is not None:
                (repr([x.encode(sys.stdout.encoding) for x in errorChars]).decode('string-escape'))
            else:
                print(errorChars)
        if max_width is not None:
            print(('For the supplied target width %(width)d the found results ranged in width from %(min)d to %(max)d' %
                  { 'width': max_width, 'min': minWordWidth, 'max': maxWordWidth }))

    if pasteboard:
        print(('%(matches)s matching words have been copied to your pasteboard. Done.' % { 'matches': min(len(results), 100) }))
    else:
        print(('%(matches)s matching words written to %(output)s. Done.' % { 'matches': len(results), 'output': output }))