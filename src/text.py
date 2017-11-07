# built-in modules
import operator

# dependency modules
import regex


def removePunctuation(text):
    return regex.sub(ur"\p{P}+", "", text)


def removeNumbers(text):
    return regex.sub(ur"\d+", "", text)


def filterByCombinations(strings, combinations):
    filtered = []
    for string in strings:
        for ngram in combinations:
            if ngram in string:
                filtered.append(string)
    return filtered


def getGlyphNameFromUnicode(unicode, glyphs):
    try:
        return glyphs[unicode]
    except KeyError:
        print("getGlyphNameFromUnicode KeyError for", unicode)
        return None


def getWordWidths(text, kerning, font, glyphs, max_width):
    widths = []
    strings = []

    for word in text:
        width = getWordWidth(word, kerning, font, glyphs)
        if max_width is None or (max_width is not None and width < max_width):
            widths.append(width)
            strings.append(word)

    return reversed(sorted(zip(strings, widths), key=lambda x: x[1]))


def getWordAndSequenceWidths(text, kerning, font, glyphs, max_width, min_width = 0):
    widths = []
    strings = []

    # for every word, check its width, and if it's below max_width, also it plus 
    # consequtive words, until it is over width
    for index, word in enumerate(text):
        string = ""
        stringWidth = 0;
        wordOffset = 0;

        while stringWidth < max_width:

            # make sure any consequtive word is actually not beyond the bounds of
            # the text array of words
            wordIndex = index + wordOffset
            if len(text) > wordIndex:
                string += " " + text[index + wordOffset]
                stringWidth = getWordWidth(string, kerning, font, glyphs)

                # if the string is not beyond the max_width, iterate further
                if stringWidth < max_width and stringWidth > min_width:
                    widths.append(stringWidth)
                    strings.append(string)

                    # finally, add a space, so added next words have a space inbetween
                    # which also gets added to their computed width
                    string += " "

                wordOffset += 1
            else:
                # if the word index is out of bound, break from the while loop
                stringWidth = max_width
    
    return reversed(sorted(zip(strings, widths), key=lambda x: x[1]))


def getWordWidth(word, kerning, font, glyphs):
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

    return wordWidth


# Reduce any duplicates from the input text (if it was natural text, as opposed to a dictionary)
# From https://www.peterbe.com/plog/uniqifiers-benchmark
# Not order preserving
def removeDuplicates(text):
    keys = {}
    for e in text:
        keys[e] = 1
    text = keys.keys()
    return text

