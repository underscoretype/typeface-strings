# dependency modules
import regex


def removePunctuation(text):
    return regex.sub(ur"\p{P}+", "", text)


def removeNumbers(text):
    return regex.sub(ur"\d+", "", text)


def getGlyphNameFromUnicode(unicode, glyphs):
    try:
        return glyphs[unicode]
    except KeyError:
        print("getGlyphNameFromUnicode KeyError for", unicode)
        return None


def getWordWidths(text, kerning, font, glyphs):
    wordWidths = []
    for word in text:

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

    return wordWidths


def getWordsWithinLimit(text, min_width, max_width, widthsAndWords, wordWidths, max_results):
    results = []
    for word, length in widthsAndWords:

        if length <= max_width:
            if min_width is None and word not in results:
                results.append(word)
            else:
                if length > min_width and word not in results:
                    results.append(word)

        if max_results is not None and len(results) >= max_results:
            break

    if results and len(results) > 0:
        maxWordWidth = wordWidths[text.index(results[0])]
        minWordWidth = wordWidths[text.index(results[-1])]
    else:
        maxWordWidth = 0
        minWordWidth = 0

    return results
