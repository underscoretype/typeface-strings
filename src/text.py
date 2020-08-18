# built-in modules
import operator

# dependency modules
# import regex
import re


def removePunctuation(text):
    return re.sub(r"\p{P}+", "", text)


def removeNumbers(text):
    return re.sub(r"\d+", "", text)


def filterByCombinations(strings, combinations):
    filtered = []
    for string in strings:
        for ngram in combinations:
            if ngram in string:
                filtered.append(string)
    return filtered


def getGlyphNameFromUnicode(str, glyphs):
    try:
        return glyphs[str]
    except KeyError:
        print(("getGlyphNameFromUnicode KeyError for", str))
        return None


def getWordWidths(text, kerning, font, glyphs, substitutions, max_width):
    widths = []
    strings = []

    for word in text:
        width = getWordWidth(word, kerning, font, glyphs, substitutions)
        if max_width is None or (max_width is not None and width < max_width):
            widths.append(width)
            strings.append(word)

    return reversed(sorted(zip(strings, widths), key=lambda x: x[1]))


def getWordAndSequenceWidths(text, kerning, font, glyphs, substitutions, max_width, min_width = 0):
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

                if string != "":
                    string += " "

                string += text[index + wordOffset]
                stringWidth = getWordWidth(string, kerning, font, glyphs, substitutions)

                # if the string is not beyond the max_width, iterate further
                if (stringWidth < max_width and stringWidth > min_width) and string not in strings:
                    widths.append(stringWidth)
                    strings.append(string)

                wordOffset += 1
            else:
                # if the word index is out of bound, break from the while loop
                stringWidth = max_width


    return reversed(sorted(zip(strings, widths), key=lambda x: x[1]))


def getWordWidth(word, kerning, font, glyphs, substitutions):
    lastLetter = None
    lastLetterWasSubstitute = False
    wordWidth = 0
    
    for index in range( len( word ) ):
        letter = word[index]

        # see if this letter is a substituted one or an actual letter
        isSubstitute = False
        glyphName = ""

        # TODO iterate this expensive re-match for each letter
        for key, sub in substitutions.items():
            pattern = re.escape(key)
            finds = re.finditer(pattern, word)

            if (finds):
                for m in finds:
                    # since there can be several hits, only get the one relevant to this index
                    if (m.start() > index + 1):
                        continue

                    isSubstitute = index >= m.start() and index < m.end()
                    substitute = sub

        try:
            if isSubstitute:
                kernValue = 0
                if not lastLetterWasSubstitute:
                    # TODO make sure this glpyh exists
                    wordWidth += font[substitute].width
                    # print "first letter of substitute, added to word width", font[substitute].width

                lastLetter = substitute

            else:
                if not lastLetter or not letter:
                    lastLetter = letter
                    continue
                
                kernValue = kerning.find((lastLetter, letter))

                glyphName = getGlyphNameFromUnicode(ord(letter), glyphs)
                wordWidth += font[glyphName].width
                lastLetter = letter

            if kernValue is not None:
                wordWidth += kernValue
            
            lastLetterWasSubstitute = isSubstitute

        except KeyError as e:
            print(("KeyError", word, glyphName, letter, ord(letter)))
            continue

    return wordWidth


# Reduce any duplicates from the input text (if it was natural text, as opposed to a dictionary)
# From https://www.peterbe.com/plog/uniqifiers-benchmark
# Not order preserving
def removeDuplicates(text):
    keys = {}
    for e in text:
        keys[e] = 1
    text = list(keys.keys())
    return text

