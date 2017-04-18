# TypeStrings

A simple CLI tool for generating sample strings from a UFO file and dictionary input.

You can use this tool when creating a preview specimen of a typeface and require words from different sources and with specific widths, all the while cross-referencing available characters from your UFO file.

## Features

* Specify a UFO file, available characters, metrics and kerning is automatically read in
* Specify any word dictionary (or other) text file to extract sample strings from
* Limit matched words by length and number of hits
* Generates an output text file with found words that can be spelled with the UFO file's charset

*Tested only on Mac OS X.* 

## Installation

To use the binary, simply copy `dist/typestrings` from this repository to a folder in your console path or make the folder available, for example grab the binary straight like this:

`$ wget https://github.com/kontur/typeface-strings/blob/master/dist/typestrings`

Make sure the file is executable, chmod to executable for your unix user if necessary.

*Unfortunately no installer or update function is available. If you are updating the script, remove any old binary or copy of the python script and follow the above installation instructions. To find the location where a previous version of the binary is located, you can use the `$ which typestrings`.*

*To use the python script and make modifications, you need to install the packages `regex` and `robofab`, for example with pip.*

## Usage

**Minimal example:**

`$ typestrings myfont.ufo samplestrings.txt`

*The minimal required input, in this order, is a path to ufo file, and a path to a text file containing sample words.

*This command returns all found matches and saves them to `myfont_samplestrings_output.txt`. A match here means any word found in the sample words that can be written with the glyphs found in the ufo file. For example, if you have a font that has characters to support only ascii english, and you have a sample text with a spanish dictionary, only those words will be matched that can be written with the ascii charset (glyphs found in the ufo file)*

**Retrieve x words of x length:**

`$ typestrings myfont.ufo samplestrings.txt -m 5 -w 5000`

*Return 5 matches that are 5000 units or just below and saves them to `myfont_samplestrings_output.txt`*

**Retrieve all words that have any of the passed in, comma-separated, ngrams:**

`$ typestrings myfont.ufo samplesstrings.txt -c an,on,alad

*Matches all words that have either the letter combination "an", "on" or "alad" in them.*

**Retrieve all words or word combinations that are less than 5000 units wide**

`$ typestring myfont.ufo samplesstrings.txt -s -w 5000`

*The -s flag (only available in conjunction with at least a -w parameter) will allow you to also match word combination or partial sentences. Note that this works best if your text sample is a natural text, not a dictionary*
 
**Retrieve all words that made up of the passed in characters**
  
`$ typestrings myfont.ufo samplestrings.txt -e "aäknoöscíBC`

*Returns words like `käännös` or `Bacon` that were made up entirely of crossreferenced characters (assuming they were in input as well as defined in the font). Note that this is quite a restrictive filter and can often result in zero matches if too many characters are passed in or the sample text is small.*

## Available parameters

* `first parameter`: Path to UFO file
* `second parameter`: Path to input word dictionary (duplicates are automatically eliminated)
* `-w` `--max-width`: Maximum width for found words, in UPM of the provided font
* `-m` `--min-width`: Minimum width for found words, in UPM of the provided font
* `-r` `--results`: Maximum results returned, when paired with `-w` in order of descending width
* `-o` `--output`: Explicitly provide output file path
* `-pb` `--pasteboard`: Copy the results to the pasteboard instead of a file. Simply `cmd + v` to paste the results (automatically limited to max 100 results)
* `-p` `--filter-punctuation`: Remove any punctuation marks from the input word dictionary
* `-n` `--filter-numbers`: Remove any numbers from the input word dictionary
* `-f` `--input-force`: Force filtering to words that only contain all of the passed in characters
* `-s` `--word-sequence`: Allow combinations of several words from the source to match a given width -w'
* `-c` `--letter-combinations`: List of comma-separated n-grams that must be found in matched strings
* `-v` `--verbose`: Output verbose information of the generation process

## Example dictionaries
Collected here a couple of places you can use for gathering comprehensive language samples to generate from. Note that increasing the input beyond 1 million words will cause significant delay in the script execution.

* [Project Gutenberg](https://www.gutenberg.org/) has text files of literary works you can use (note the `-p` flag to strip punctuation) - make sure the file is saved in UTF-8
* *Other suggestions welcome, just edit this documentation file and add ;)*

You can also collect your own word samples with nice kerning pairs, plenty of language specific characters or your custom preference of languages in one file.

### License
Released under [MIT license](LICENSE.txt) - You can do with this software what you want, but you are required to provide this copyright and license notices.

Copyright 2017 Johannes 'kontur' Neumeier

### Issues
* Make sure you are supplying the input in a utf8 encoded file

### Planned features
* Support inputting .glyph files, output a file for each master
* Support inputting .otf files
* Support inputting .ttf files
* Algorithm to pick words for maximal diverse character selection when used with `-m`
* Option to cast the input to UPPERCASE, lowercase, Mixedcase words

Contribution in form of feature requests, bug reports and pull requests most welcome. Let me know what's on your mind ;)