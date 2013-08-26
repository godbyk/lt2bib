#!/usr/bin/python
# vim:shiftwidth=4:tabstop=4:expandtab:filetype=python

# Author:
#   Kevin Godby <godbyk@gmail.com>
#
# License:
#   Public domain.

"""
lt2bib.py is a script that parses the files exported by LibraryThing and
generates a BiBTeX file with the same information.

Usage: lt2bib.py <tab-delimited-file>

The <tab-delimited-file> is exported from LibraryThing.
"""

import sys, codecs, re

if len(sys.argv) < 2:
    print "Usage:", sys.argv[0], "[-l]", "<tab-delimited file>"
    print "\t-l\tGenerates a LaTeX file that tests the BibTeX file."
    print "\nExample:", sys.argv[0], "LibraryThing_TD.xls"

    sys.exit(1)


def clean(x):
    x = x.replace("&", "\\&")
    return x


def valid_key(bib_dict, key):
    # if the bib_dict is empty, return the key
    if bib_dict.keys() == []:
        return key

    # add all similar keys to the existing_keys list
    existing_keys = []
    for k in bib_dict.keys():
        if k is None:
            continue

        if k.lower().startswith(key.lower()):
            existing_keys.append(k)

    # find the latest key appendix
    max_postfix = ''
    for k in existing_keys:
        key_parts = re.split(r'[0-9]+', k)
        if len(key_parts[-1]) > len(max_postfix):
            max_postfix = key_parts[-1]
        elif len(key_parts[-1]) == len(max_postfix):
            if key_parts > max_postfix:
                max_postfix = key_parts[-1]

    # generate new key with incremented postfix
    key = key + nextpostfix(max_postfix)

    return key
        
def nextpostfix(x):
    """Returns the next alpha postfix in the sequence."""
    if x == '':
        return 'a'

    if ord(x[-1]) < ord('z'):
        x = x[0:-1] + chr(ord(x[-1])+1)
    else:
        if x[0] == 'z':
            x = 'a' + 'a' * len(x)
        else:
            x = chr(ord(x[0])+1) + x[1:]
            x = x[0:-1] + 'a'
    return x

def parseEdition(x):
    """Takes an integer and returns a ordinal word."""
    ordinal_dict = {
        1 : 'First', 
        2 : 'Second', 
        3 : 'Third', 
        4 : 'Fourth', 
        5 : 'Fifth', 
        6 : 'Sixth', 
        7 : 'Seventh', 
        8 : 'Eighth', 
        9 : 'Ninth', 
        10 : 'Tenth', 
        11 : 'Eleventh', 
        12 : 'Twelfth', 
        13 : 'Thirteenth', 
        14 : 'Fourteenth', 
        15 : 'Fifteenth', 
        16 : 'Sixteenth', 
        17 : 'Seventeenth', 
        18 : 'Eighteenth', 
        19 : 'Nineteenth', 
        20 : 'Twentieth', 
        21 : 'Twenty-first', 
        22 : 'Twenty-second', 
        23 : 'Twenty-third', 
        24 : 'Twenty-fourth', 
        25 : 'Twenty-fifth', 
        26 : 'Twenty-sixth', 
        27 : 'Twenty-seventh', 
        28 : 'Twenty-eighth', 
        29 : 'Twenty-ninth', 
        30 : 'Thirtieth', 
        31 : 'Thirty-first', 
        32 : 'Thirty-second', 
        100 : 'Hundredth', 
        101 : 'Hundred and first', 
        112 : 'Hundred and twelfth', 
        1000 : 'Thousandth ', 
    }

    if int(x) in ordinal_dict:
        return ordinal_dict[int(x)]
    else:
        print "didn't find ordinal:", x
        return x


# ==================== MAIN LOOP =========================================

# Open the bookdata.csv file
latex = False
for arg in sys.argv:
    if arg[0] != '-':
        input_file = arg
    if arg == "-l":
        latex = True

bookdata = codecs.open(input_file, 'rb', 'utf-16')
lines = bookdata.readlines()

bibtex_file = file("LibraryThing.bib", 'w')

if latex:
    latex_file = file("LibraryThing.tex", 'w')
    latex_file.write("""
\\documentclass{article}
\\usepackage{apacite}
\\title{Test of the \\texttt{LibraryThing.bib} file}
\\begin{document}
\\begin{itemize}
""")

#bibtex_file.write("line\n")

bib_dict = { }
linenum = -1 
for l in lines:
    linenum = linenum + 1
    if 0 == linenum:
        continue
   
    line = l.split('\t')

    # [u'6268961', u'Writing Winning Business Proposals: Your Guide to
    # Landing the Client, Making the Sale and Persuading the Boss', u'Richard
    # C. Freed', u'Freed, Richard C.', u'Joe Romano', u'McGraw-Hill (2003),
    # Edition: 2, Paperback', u'2003', u'[007139687X]', u'', u'Amazon.com',
    # u'English', u'(blank)', u'(blank)', u'', u'', u'', u'Sep 3, 2006', u'',
    # u'', u'', u'', u'', u'', u'Writing Winning Business Proposals: Your
    # Guide to Landing the Client, Making the Sale and Persuading the Boss by
    # Richard C. Freed (2003)', u'', u'ASCII', u'\r\n']

    book_id       = line[0]  # book id
    title         = clean(line[1])  # title
    author_fl     = line[2]  # author, first-last
    author_lf     = line[3]  # author, last-first
    other_authors = line[4]  # other authers
    publication   = clean(line[5])  # publication
    date          = line[6]  # date
    isbn          = line[7]  # ISBN
    series        = line[8]  # series
    source        = line[9]  # source
    lang1         = line[10] # language 1
    lang2         = line[11] # language 2
    lang_orig     = line[12] # original language
    lc_call_num   = line[13] # LC call number
    dewey_decimal = line[14] # Dewey decimal number
    bcid          = line[15] # BCID
    date1         = line[16] # date entered
    date2         = line[17] # date entered
    date3         = line[18] # date entered
    date4         = line[19] # date entered
    tags          = line[20] # tags
    rating        = line[21] # rating
    review        = line[22] # review
    summary       = clean(line[23]) # summary
    comments      = line[24] # comments
    encoding      = line[25] # encoding

    author = author_fl
    
    # Name of editor, typed as indicated in the LaTeX book. If there is a
    # also an author field, then the editor field gives the editor of the book
    # or collection in which the reference appears.
    editor = ""
    
    # DEBUG
    # publication is like:
    #    McGraw-Hill (2003), Edition: 2, Paperback
    #    Penguin (Non-Classics) (2002), Edition: Reprint, Paperback
    publication_info = publication.split(",")

    # The publisher's name.
    publisher = publication_info[0].strip()[:-6].strip()

    # The year of publication or, for an unpublished work, the year it was
    # written. Generally it should consist of four numerals, such as 1984,
    # although the standard styles can handle any year whose last four
    # nonpunctuation characters are numerals, such as '(about 1984)'.
    year = date

    # Usually the address of the publisher or other type of institution.
    # For major publishing houses, van Leunen recommends omitting the
    # information entirely. For small publishers, on the other hand, you
    # can help the reader by giving the complete address.
    address = ""
    
    # In the format of 'First', 'Second', etc.  This should be an ordinal,
    # and should have the first letter capitalized, as shown here; the
    # standard styles convert to lower case when necessary.
    edition = ""
    if publication_info[1].strip().startswith('Edition:'):
        edition = publication_info[1].strip()[9:].strip().split(',')[0]
        m = re.compile("(\d+)", re.M).search(edition)
        if m is not None:
            edition = parseEdition(m.group(1))

    # The volume of a journal or multivolume book.
    volume = ""

    # The number of a journal, magazine, technical report, or of a
    # work in a series. An issue of a journal or magazine is usually
    # identified by its volume and number; the organization that issues a
    # technical report usually gives it a number; and sometimes books are
    # given numbers in a named series.
    number = ""

    # The name of a series or set of books. When citing an entire book,
    # the the title field gives its title and an optional series field gives
    # the name of a series or multi-volume set in which the book is
    # published.
    series = ""

    # The month in which the work was published or, for an unpublished
    # work, in which it was written. You should use the standard three-letter
    # abbreviation, as described in Appendix B.1.3 of the LaTeX book.
    month = ""

    # Any additional information that can help the reader. The first word
    # should be capitalized.
    note = comments

    otherinfo = "ISBN " + isbn[1:-1]

    # Calculate the key (usually author's last name + 4-digit year)
    if author == '':
        if editor == '':
            print "Warning: %s has no author or editor!" % (title)
            key = "UnknownAuthor" + date
        else:
            key = editor + date
    else:
        key = author_lf.split(',')[0] + date

    key = valid_key(bib_dict, key)

    # add to bib_dict
    bib_dict[key] = {
        'author' : author,
        'editor' : editor,
        'title' : title,
        'publisher' : publisher,
        'year' : year,
        'address' : address,
        'edition' : edition,
        'volume' : volume,
        'number' : number,
        'series' : series,
        'month' : month,
        'note' : note,
        'isbn' : isbn,
        'otherinfo' : otherinfo
    }


    bibtex_file.write("""
@BOOK{%s,
\tauthor = {%s},
\teditor = {%s},
\ttitle = {%s},
\tpublisher = {%s},
\tyear = {%s},
\taddress = {%s},
\tedition = {%s},
\tvolume = {%s},
\tnumber = {%s},
\tseries = {%s},
\tmonth = {%s},
\tnote = {%s},
\totherinfo = {%s},
\tisbn = {%s}
}
}
""" % (key, author, editor, title, publisher, year, address, edition,
    volume, number, series, month, note, isbn, otherinfo))

    if latex:
        latex_file.write("\\item %s \\cite{%s}\n" % (title, key))

# Close the BiBTeX file
bibtex_file.close()

# Close the LaTeX file
if latex:
    latex_file.write("""
\\end{itemize}
\n\n
\\bibliographystyle{apacite}
\\bibliography{LibraryThing}
\\end{document}
""")
    latex_file.close()
