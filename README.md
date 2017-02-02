# TypeStrings

A simple CLI tool for generating sample strings from a UFO file and dictionary input.

You can use this tool when creating a preview specimen of a typeface and require words from different sources and with specific widths, all the while cross-referencing available characters from your UFO file.

## Features

* Specify a UFO file, available characters, metrics and kerning is automatically read in
* Specify any word dictionary (or other) text file to extract sample strings from
* Limit matched words by length and number of hits
* Generates an output text file with found words that can be spelled with the UFO file's charset

## Installation

To use the binary, simply copy `dist/typestrings` from this repository to a folder in your console path or make the folder available, for example grab the binary straight like this:

`$ wget https://github.com/kontur/typeface-strings/blob/master/dist/typestrings`

Make sure the file is executable, chmod if necessary.

*To use the python script and make modifications, you need to install the packages `regex` and `robofab`, for example with pip.*

## Usage

**Minimal example:**

`$ typestrings -f "myfont.ufo" -i "samplestrings.txt`

*Returns all found matches and saves them to `myfont_samplestrings_output.txt`*

**Retrieve x words of x length:**

`$ typestrings -f "myfont.ufo" -i "samplestrings.txt" -m 5 -w 5000`

*Return 5 matches that are 5000 units or just below and saves them to `myfont_samplestrings_output.txt`*
 
**Retrieve all words that made up of the passed in characters**
  
`$ typestrings -f "myfont.ufo" -i "samplestrings.txt" -e "aäknoöscíBC`

*Returns words like `käännös` or `Bacon` that were made up entirely of crossreferenced characters (assuming they were in input as well as defined in the font)*

## Available parameters

* `-f` `--font`: Path to UFO file
* `-i` `--input`: Path to input word dictionary
* `-w` `--max-width`: Maximum width for found words, in UPM of the provided font
* `-m` `--min-width`: Minimum width for found words, in UPM of the provided font
* `-r` `--results`: Maximum results returned, when paired with `-w` in order of descending width
* `-o` `--output`: Explicitly provide output file path
* `-p` `--filter-punctuation`: Remove any punctuation marks from the input word dictionary
* `-n` `--filter-numbers`: Remove any numbers from the input word dictionary
* `-e` `--input-force`: Force filtering to words that only contain all of the passed in characters
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
* Create compound strings for widths that strings are not long enough when used with `-w`
* Algorithm to pick words for maximal diverse character selection when used with `-m`
* Option to cast the input to UPPERCASE, lowercase, Mixedcase words
* (Partially done) Option to force inclusion or exclusion of a set of characters, either as string or separate file

Contribution in form of feature requests, bug reports and pull requests most welcome. Let me know what's on your mind ;)