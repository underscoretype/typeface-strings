# TypeStrings

A simple CLI tool for generating sample strings from a UFO file and dictionary input.

You can use this tool when creating a preview specimen of a typeface and require words from different sources and with specific widths, all the while cross-referencing available characters from your UFO file.

## Features

* Specify a UFO file, available characters, metrics and kerning is automatically read in
* Specify any word dictionary (or other) text file to extract sample strings from
* Limit matched words by length and number of hits
* Generates an output text file with found words that can be spelled with the UFO file's charset

## Installation

## Usage

**Minimal example:**

`$ typestrings -f "myfont.ufo" -i "samplestrings.txt`

*Returns all found matches and saves them to `myfont_samplestrings_output.txt`*

**Retrieve x words of x length:**

`$ typestrings -f "myfont.ufo" -i "samplestrings.txt" -m 5 -w 5000`

*Return 5 matches that are 5000 units or just below and saves them to `myfont_samplestrings_output.txt`* 

## Available parameters

* `-f` `--font`: Path to UFO file
* `-i` `--input`: Path to input word dictionary
* `-w` `--max-width`: Maximum width for found words, in UPM of the provided font
* `-m` `--min-width`: Minimum width for found words, in UPM of the provided font
* `-r` `--results`: Maximum results returned, when paired with `-w` in order of descending width
* `-o` `--output`: Explicitly provide output file path
* `-p` `--filter-punctuation`: Remove any punctuation marks from the input word dictionary
* `-v` `--verbose`: Output verbose information of the generation process

### License
Released under [MIT license](LICENSE.txt) - You can do with this software what you want, but you are required to provide this copyright and license notices.

Copyright 2017 Johannes 'kontur' Neumeier

### Issues
* Make sure you are supplying the input in a utf8 encoded file

### Planned features
* Support inputting .glyph files, output a file for each master
* Create compound strings for widths that strings are not long enough when used with `-w`
* Algorithm to pick words for maximal diverse character selection when used with `-m`
* Option to filter numbers similar to `-p`
* Option to cast the input to UPPERCASE, lowercase, Mixedcase words
* Option to force inclusion or exclusion of a set of characters, either as string or separate file