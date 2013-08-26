#!/usr/bin/env python
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

import sys, codecs, re, os
import datetime
import cgi

import cgitb; cgitb.enable()    # XXX for debugging

# textescmap and textmap are from specmap.py in the TexML package:
#   http://getfo.org/texml/
# and used under TexML's MIT/X11 license

textescmap = {
  '\\': r'\textbackslash{}',
  '{':  r'\{',
  '}':  r'\}',
  '$':  r'\textdollar{}',
  '&':  r'\&',
  '#':  r'\#',
  '^':  r'\^{}',
  '_':  r'\_',
  '~':  r'\textasciitilde{}',
  '%':  r'\%',
  '|':  r'\textbar{}',
  '<':  r'\textless{}',
  '>':  r'\textgreater{}',
  # not special but typography
  u'\u00a9': r'\textcopyright{}',
  u'\u2011': r'\mbox{-}'
}

textmap = {
0x000A0: r'~',
0x000AD: r'\-',
0x0007E: r'\textasciitilde{}',
0x000A1: r'\textexclamdown{}',
0x000A2: r'\textcent{}',
0x000A3: r'\textsterling{}',
0x000A4: r'\textcurrency{}',
0x000A5: r'\textyen{}',
0x000A6: r'\textbrokenbar{}',
0x000A7: r'\textsection{}',
0x000A8: r'\textasciidieresis{}',
0x000A9: r'\textcopyright{}',
0x000AA: r'\textordfeminine{}',
0x000AB: r'\guillemotleft{}',
0x000AE: r'\textregistered{}',
0x000AF: r'\textasciimacron{}',
0x000B0: r'\textdegree{}',
0x000B4: r'\textasciiacute{}',
0x000B6: r'\textparagraph{}',
0x000B8: r'\c{}',
0x000BA: r'\textordmasculine{}',
0x000BB: r'\guillemotright{}',
0x000BC: r'\textonequarter{}',
0x000BD: r'\textonehalf{}',
0x000BE: r'\textthreequarters{}',
0x000BF: r'\textquestiondown{}',
0x000C0: r'\`{A}',
0x000C1: r"\'{A}",
0x000C2: r'\^{A}',
0x000C3: r'\~{A}',
0x000C4: r'\"{A}',
0x000C5: r'\AA{}',
0x000C6: r'\AE{}',
0x000C7: r'\c{C}',
0x000C8: r'\`{E}',
0x000C9: r"\'{E}",
0x000CA: r'\^{E}',
0x000CB: r'\"{E}',
0x000CC: r'\`{I}',
0x000CD: r"\'{I}",
0x000CE: r'\^{I}',
0x000CF: r'\"{I}',
0x000D0: r'\DH{}',
0x000D1: r'\~{N}',
0x000D2: r'\`{O}',
0x000D3: r"\'{O}",
0x000D4: r'\^{O}',
0x000D5: r'\~{O}',
0x000D6: r'\"{O}',
0x000D7: r'\texttimes{}',
0x000D8: r'\O{}',
0x000D9: r'\`{U}',
0x000DA: r"\'{U}",
0x000DB: r'\^{U}',
0x000DC: r'\"{U}',
0x000DD: r"\'{Y}",
0x000DE: r'\TH{}',
0x000DF: r'\ss{}',
0x000E0: r'\`{a}',
0x000E1: r"\'{a}",
0x000E2: r'\^{a}',
0x000E3: r'\~{a}',
0x000E4: r'\"{a}',
0x000E5: r'\aa{}',
0x000E6: r'\ae{}',
0x000E7: r'\c{c}',
0x000E8: r'\`{e}',
0x000E9: r"\'{e}",
0x000EA: r'\^{e}',
0x000EB: r'\"{e}',
0x000EC: r'\`{\i}',
0x000ED: r"\'{\i}",
0x000EE: r'\^{\i}',
0x000EF: r'\"{\i}',
0x000F0: r'\dh{}',
0x000F1: r'\~{n}',
0x000F2: r'\`{o}',
0x000F3: r"\'{o}",
0x000F4: r'\^{o}',
0x000F5: r'\~{o}',
0x000F6: r'\"{o}',
0x000F8: r'\o{}',
0x000F9: r'\`{u}',
0x000FA: r"\'{u}",
0x000FB: r'\^{u}',
0x000FC: r'\"{u}',
0x000FD: r"\'{y}",
0x000FE: r'\th{}',
0x000FF: r'\"{y}',
0x00100: r'\={A}',
0x00101: r'\={a}',
0x00102: r'\u{A}',
0x00103: r'\u{a}',
0x00104: r'\k{A}',
0x00105: r'\k{a}',
0x00106: r"\'{C}",
0x00107: r"\'{c}",
0x00108: r'\^{C}',
0x00109: r'\^{c}',
0x0010A: r'\.{C}',
0x0010B: r'\.{c}',
0x0010C: r'\v{C}',
0x0010D: r'\v{c}',
0x0010E: r'\v{D}',
0x0010F: r'\v{d}',
0x00110: r'\DJ{}',
0x00111: r'\dj{}',
0x00112: r'\={E}',
0x00113: r'\={e}',
0x00114: r'\u{E}',
0x00115: r'\u{e}',
0x00116: r'\.{E}',
0x00117: r'\.{e}',
0x00118: r'\k{E}',
0x00119: r'\k{e}',
0x0011A: r'\v{E}',
0x0011B: r'\v{e}',
0x0011C: r'\^{G}',
0x0011D: r'\^{g}',
0x0011E: r'\u{G}',
0x0011F: r'\u{g}',
0x00120: r'\.{G}',
0x00121: r'\.{g}',
0x00122: r'\c{G}',
0x00123: r'\c{g}',
0x00124: r'\^{H}',
0x00125: r'\^{h}',
0x00126: r'{\fontencoding{LELA}\selectfont\char40}',
0x00128: r'\~{I}',
0x00129: r'\~{\i}',
0x0012A: r'\={I}',
0x0012B: r'\={\i}',
0x0012C: r'\u{I}',
0x0012D: r'\u{\i}',
0x0012E: r'\k{I}',
0x0012F: r'\k{i}',
0x00130: r'\.{I}',
0x00131: r'\i{}',
0x00132: r'IJ',
0x00133: r'ij',
0x00134: r'\^{J}',
0x00135: r'\^{\j}',
0x00136: r'\c{K}',
0x00137: r'\c{k}',
0x00138: r'{\fontencoding{LELA}\selectfont\char91}',
0x00139: r"\'{L}",
0x0013A: r"\'{l}",
0x0013B: r'\c{L}',
0x0013C: r'\c{l}',
0x0013D: r'\v{L}',
0x0013E: r'\v{l}',
0x0013F: r'{\fontencoding{LELA}\selectfont\char201}',
0x00140: r'{\fontencoding{LELA}\selectfont\char202}',
0x00141: r'\L{}',
0x00142: r'\l{}',
0x00143: r"\'{N}",
0x00144: r"\'{n}",
0x00145: r'\c{N}',
0x00146: r'\c{n}',
0x00147: r'\v{N}',
0x00148: r'\v{n}',
0x00149: r"'n",
0x0014A: r'\NG{}',
0x0014B: r'\ng{}',
0x0014C: r'\={O}',
0x0014D: r'\={o}',
0x0014E: r'\u{O}',
0x0014F: r'\u{o}',
0x00150: r'\H{O}',
0x00151: r'\H{o}',
0x00152: r'\OE{}',
0x00153: r'\oe{}',
0x00154: r"\'{R}",
0x00155: r"\'{r}",
0x00156: r'\c{R}',
0x00157: r'\c{r}',
0x00158: r'\v{R}',
0x00159: r'\v{r}',
0x0015A: r"\'{S}",
0x0015B: r"\'{s}",
0x0015C: r'\^{S}',
0x0015D: r'\^{s}',
0x0015E: r'\c{S}',
0x0015F: r'\c{s}',
0x00160: r'\v{S}',
0x00161: r'\v{s}',
0x00162: r'\c{T}',
0x00163: r'\c{t}',
0x00164: r'\v{T}',
0x00165: r'\v{t}',
0x00166: r'{\fontencoding{LELA}\selectfont\char47}',
0x00167: r'{\fontencoding{LELA}\selectfont\char63}',
0x00168: r'\~{U}',
0x00169: r'\~{u}',
0x0016A: r'\={U}',
0x0016B: r'\={u}',
0x0016C: r'\u{U}',
0x0016D: r'\u{u}',
0x0016E: r'\r{U}',
0x0016F: r'\r{u}',
0x00170: r'\H{U}',
0x00171: r'\H{u}',
0x00172: r'\k{U}',
0x00173: r'\k{u}',
0x00174: r'\^{W}',
0x00175: r'\^{w}',
0x00176: r'\^{Y}',
0x00177: r'\^{y}',
0x00178: r'\"{Y}',
0x00179: r"\'{Z}",
0x0017A: r"\'{z}",
0x0017B: r'\.{Z}',
0x0017C: r'\.{z}',
0x0017D: r'\v{Z}',
0x0017E: r'\v{z}',
0x00195: r'\texthvlig{}',
0x0019E: r'\textnrleg{}',
0x001BA: r'{\fontencoding{LELA}\selectfont\char195}',
0x001C2: r'\textdoublepipe{}',
0x001F5: r"\'{g}",
0x00258: r'{\fontencoding{LEIP}\selectfont\char61}',
0x00261: r'g',
0x00272: r'\Elzltln{}',
0x00278: r'\textphi{}',
0x0027F: r'{\fontencoding{LEIP}\selectfont\char202}',
0x0029E: r'\textturnk{}',
0x002BC: r"'",
0x002C7: r'\textasciicaron{}',
0x002D8: r'\textasciibreve{}',
0x002D9: r'\textperiodcentered{}',
0x002DA: r'\r{}',
0x002DB: r'\k{}',
0x002DC: r'\texttildelow{}',
0x002DD: r'\H{}',
0x002E5: r'\tone{55}',
0x002E6: r'\tone{44}',
0x002E7: r'\tone{33}',
0x002E8: r'\tone{22}',
0x002E9: r'\tone{11}',
0x00300: r'\`',
0x00301: r"\'",
0x00302: r'\^',
0x00303: r'\~',
0x00304: r'\=',
0x00306: r'\u{}',
0x00307: r'\.',
0x00308: r'\"',
0x0030A: r'\r{}',
0x0030B: r'\H{}',
0x0030C: r'\v{}',
0x0030F: r'\cyrchar\C{}',
0x00311: r'{\fontencoding{LECO}\selectfont\char177}',
0x00318: r'{\fontencoding{LECO}\selectfont\char184}',
0x00319: r'{\fontencoding{LECO}\selectfont\char185}',
0x00322: r'\Elzrh{}',
0x00327: r'\c{}',
0x00328: r'\k{}',
0x0032B: r'{\fontencoding{LECO}\selectfont\char203}',
0x0032F: r'{\fontencoding{LECO}\selectfont\char207}',
0x00335: r'\Elzxl{}',
0x00336: r'\Elzbar{}',
0x00337: r'{\fontencoding{LECO}\selectfont\char215}',
0x00338: r'{\fontencoding{LECO}\selectfont\char216}',
0x0033A: r'{\fontencoding{LECO}\selectfont\char218}',
0x0033B: r'{\fontencoding{LECO}\selectfont\char219}',
0x0033C: r'{\fontencoding{LECO}\selectfont\char220}',
0x0033D: r'{\fontencoding{LECO}\selectfont\char221}',
0x00361: r'{\fontencoding{LECO}\selectfont\char225}',
0x00386: r"\'{A}",
0x00388: r"\'{E}",
0x00389: r"\'{H}",
0x0038A: r"\'{}{I}",
0x0038C: r"\'{}O{}",
0x003AC: r"\'{$\alpha$}",
0x003B8: r'\texttheta{}',
0x003CC: r"\'{o}",
0x003D0: r'\Pisymbol{ppi022}{87}',
0x003D1: r'\textvartheta{}',
0x003F4: r'\textTheta{}',
0x00401: r'\cyrchar\CYRYO{}',
0x00402: r'\cyrchar\CYRDJE{}',
0x00403: r"\cyrchar{\'\CYRG}",
0x00404: r'\cyrchar\CYRIE{}',
0x00405: r'\cyrchar\CYRDZE{}',
0x00406: r'\cyrchar\CYRII{}',
0x00407: r'\cyrchar\CYRYI{}',
0x00408: r'\cyrchar\CYRJE{}',
0x00409: r'\cyrchar\CYRLJE{}',
0x0040A: r'\cyrchar\CYRNJE{}',
0x0040B: r'\cyrchar\CYRTSHE{}',
0x0040C: r"\cyrchar{\'\CYRK}",
0x0040E: r'\cyrchar\CYRUSHRT{}',
0x0040F: r'\cyrchar\CYRDZHE{}',
0x00410: r'\cyrchar\CYRA{}',
0x00411: r'\cyrchar\CYRB{}',
0x00412: r'\cyrchar\CYRV{}',
0x00413: r'\cyrchar\CYRG{}',
0x00414: r'\cyrchar\CYRD{}',
0x00415: r'\cyrchar\CYRE{}',
0x00416: r'\cyrchar\CYRZH{}',
0x00417: r'\cyrchar\CYRZ{}',
0x00418: r'\cyrchar\CYRI{}',
0x00419: r'\cyrchar\CYRISHRT{}',
0x0041A: r'\cyrchar\CYRK{}',
0x0041B: r'\cyrchar\CYRL{}',
0x0041C: r'\cyrchar\CYRM{}',
0x0041D: r'\cyrchar\CYRN{}',
0x0041E: r'\cyrchar\CYRO{}',
0x0041F: r'\cyrchar\CYRP{}',
0x00420: r'\cyrchar\CYRR{}',
0x00421: r'\cyrchar\CYRS{}',
0x00422: r'\cyrchar\CYRT{}',
0x00423: r'\cyrchar\CYRU{}',
0x00424: r'\cyrchar\CYRF{}',
0x00425: r'\cyrchar\CYRH{}',
0x00426: r'\cyrchar\CYRC{}',
0x00427: r'\cyrchar\CYRCH{}',
0x00428: r'\cyrchar\CYRSH{}',
0x00429: r'\cyrchar\CYRSHCH{}',
0x0042A: r'\cyrchar\CYRHRDSN{}',
0x0042B: r'\cyrchar\CYRERY{}',
0x0042C: r'\cyrchar\CYRSFTSN{}',
0x0042D: r'\cyrchar\CYREREV{}',
0x0042E: r'\cyrchar\CYRYU{}',
0x0042F: r'\cyrchar\CYRYA{}',
0x00430: r'\cyrchar\cyra{}',
0x00431: r'\cyrchar\cyrb{}',
0x00432: r'\cyrchar\cyrv{}',
0x00433: r'\cyrchar\cyrg{}',
0x00434: r'\cyrchar\cyrd{}',
0x00435: r'\cyrchar\cyre{}',
0x00436: r'\cyrchar\cyrzh{}',
0x00437: r'\cyrchar\cyrz{}',
0x00438: r'\cyrchar\cyri{}',
0x00439: r'\cyrchar\cyrishrt{}',
0x0043A: r'\cyrchar\cyrk{}',
0x0043B: r'\cyrchar\cyrl{}',
0x0043C: r'\cyrchar\cyrm{}',
0x0043D: r'\cyrchar\cyrn{}',
0x0043E: r'\cyrchar\cyro{}',
0x0043F: r'\cyrchar\cyrp{}',
0x00440: r'\cyrchar\cyrr{}',
0x00441: r'\cyrchar\cyrs{}',
0x00442: r'\cyrchar\cyrt{}',
0x00443: r'\cyrchar\cyru{}',
0x00444: r'\cyrchar\cyrf{}',
0x00445: r'\cyrchar\cyrh{}',
0x00446: r'\cyrchar\cyrc{}',
0x00447: r'\cyrchar\cyrch{}',
0x00448: r'\cyrchar\cyrsh{}',
0x00449: r'\cyrchar\cyrshch{}',
0x0044A: r'\cyrchar\cyrhrdsn{}',
0x0044B: r'\cyrchar\cyrery{}',
0x0044C: r'\cyrchar\cyrsftsn{}',
0x0044D: r'\cyrchar\cyrerev{}',
0x0044E: r'\cyrchar\cyryu{}',
0x0044F: r'\cyrchar\cyrya{}',
0x00451: r'\cyrchar\cyryo{}',
0x00452: r'\cyrchar\cyrdje{}',
0x00453: r"\cyrchar{\'\cyrg}",
0x00454: r'\cyrchar\cyrie{}',
0x00455: r'\cyrchar\cyrdze{}',
0x00456: r'\cyrchar\cyrii{}',
0x00457: r'\cyrchar\cyryi{}',
0x00458: r'\cyrchar\cyrje{}',
0x00459: r'\cyrchar\cyrlje{}',
0x0045A: r'\cyrchar\cyrnje{}',
0x0045B: r'\cyrchar\cyrtshe{}',
0x0045C: r"\cyrchar{\'\cyrk}",
0x0045E: r'\cyrchar\cyrushrt{}',
0x0045F: r'\cyrchar\cyrdzhe{}',
0x00460: r'\cyrchar\CYROMEGA{}',
0x00461: r'\cyrchar\cyromega{}',
0x00462: r'\cyrchar\CYRYAT{}',
0x00464: r'\cyrchar\CYRIOTE{}',
0x00465: r'\cyrchar\cyriote{}',
0x00466: r'\cyrchar\CYRLYUS{}',
0x00467: r'\cyrchar\cyrlyus{}',
0x00468: r'\cyrchar\CYRIOTLYUS{}',
0x00469: r'\cyrchar\cyriotlyus{}',
0x0046A: r'\cyrchar\CYRBYUS{}',
0x0046C: r'\cyrchar\CYRIOTBYUS{}',
0x0046D: r'\cyrchar\cyriotbyus{}',
0x0046E: r'\cyrchar\CYRKSI{}',
0x0046F: r'\cyrchar\cyrksi{}',
0x00470: r'\cyrchar\CYRPSI{}',
0x00471: r'\cyrchar\cyrpsi{}',
0x00472: r'\cyrchar\CYRFITA{}',
0x00474: r'\cyrchar\CYRIZH{}',
0x00478: r'\cyrchar\CYRUK{}',
0x00479: r'\cyrchar\cyruk{}',
0x0047A: r'\cyrchar\CYROMEGARND{}',
0x0047B: r'\cyrchar\cyromegarnd{}',
0x0047C: r'\cyrchar\CYROMEGATITLO{}',
0x0047D: r'\cyrchar\cyromegatitlo{}',
0x0047E: r'\cyrchar\CYROT{}',
0x0047F: r'\cyrchar\cyrot{}',
0x00480: r'\cyrchar\CYRKOPPA{}',
0x00481: r'\cyrchar\cyrkoppa{}',
0x00482: r'\cyrchar\cyrthousands{}',
0x00488: r'\cyrchar\cyrhundredthousands{}',
0x00489: r'\cyrchar\cyrmillions{}',
0x0048C: r'\cyrchar\CYRSEMISFTSN{}',
0x0048D: r'\cyrchar\cyrsemisftsn{}',
0x0048E: r'\cyrchar\CYRRTICK{}',
0x0048F: r'\cyrchar\cyrrtick{}',
0x00490: r'\cyrchar\CYRGUP{}',
0x00491: r'\cyrchar\cyrgup{}',
0x00492: r'\cyrchar\CYRGHCRS{}',
0x00493: r'\cyrchar\cyrghcrs{}',
0x00494: r'\cyrchar\CYRGHK{}',
0x00495: r'\cyrchar\cyrghk{}',
0x00496: r'\cyrchar\CYRZHDSC{}',
0x00497: r'\cyrchar\cyrzhdsc{}',
0x00498: r'\cyrchar\CYRZDSC{}',
0x00499: r'\cyrchar\cyrzdsc{}',
0x0049A: r'\cyrchar\CYRKDSC{}',
0x0049B: r'\cyrchar\cyrkdsc{}',
0x0049C: r'\cyrchar\CYRKVCRS{}',
0x0049D: r'\cyrchar\cyrkvcrs{}',
0x0049E: r'\cyrchar\CYRKHCRS{}',
0x0049F: r'\cyrchar\cyrkhcrs{}',
0x004A0: r'\cyrchar\CYRKBEAK{}',
0x004A1: r'\cyrchar\cyrkbeak{}',
0x004A2: r'\cyrchar\CYRNDSC{}',
0x004A3: r'\cyrchar\cyrndsc{}',
0x004A4: r'\cyrchar\CYRNG{}',
0x004A5: r'\cyrchar\cyrng{}',
0x004A6: r'\cyrchar\CYRPHK{}',
0x004A7: r'\cyrchar\cyrphk{}',
0x004A8: r'\cyrchar\CYRABHHA{}',
0x004A9: r'\cyrchar\cyrabhha{}',
0x004AA: r'\cyrchar\CYRSDSC{}',
0x004AB: r'\cyrchar\cyrsdsc{}',
0x004AC: r'\cyrchar\CYRTDSC{}',
0x004AD: r'\cyrchar\cyrtdsc{}',
0x004AE: r'\cyrchar\CYRY{}',
0x004AF: r'\cyrchar\cyry{}',
0x004B0: r'\cyrchar\CYRYHCRS{}',
0x004B1: r'\cyrchar\cyryhcrs{}',
0x004B2: r'\cyrchar\CYRHDSC{}',
0x004B3: r'\cyrchar\cyrhdsc{}',
0x004B4: r'\cyrchar\CYRTETSE{}',
0x004B5: r'\cyrchar\cyrtetse{}',
0x004B6: r'\cyrchar\CYRCHRDSC{}',
0x004B7: r'\cyrchar\cyrchrdsc{}',
0x004B8: r'\cyrchar\CYRCHVCRS{}',
0x004B9: r'\cyrchar\cyrchvcrs{}',
0x004BA: r'\cyrchar\CYRSHHA{}',
0x004BB: r'\cyrchar\cyrshha{}',
0x004BC: r'\cyrchar\CYRABHCH{}',
0x004BD: r'\cyrchar\cyrabhch{}',
0x004BE: r'\cyrchar\CYRABHCHDSC{}',
0x004BF: r'\cyrchar\cyrabhchdsc{}',
0x004C0: r'\cyrchar\CYRpalochka{}',
0x004C3: r'\cyrchar\CYRKHK{}',
0x004C4: r'\cyrchar\cyrkhk{}',
0x004C7: r'\cyrchar\CYRNHK{}',
0x004C8: r'\cyrchar\cyrnhk{}',
0x004CB: r'\cyrchar\CYRCHLDSC{}',
0x004CC: r'\cyrchar\cyrchldsc{}',
0x004D4: r'\cyrchar\CYRAE{}',
0x004D5: r'\cyrchar\cyrae{}',
0x004D8: r'\cyrchar\CYRSCHWA{}',
0x004D9: r'\cyrchar\cyrschwa{}',
0x004E0: r'\cyrchar\CYRABHDZE{}',
0x004E1: r'\cyrchar\cyrabhdze{}',
0x004E8: r'\cyrchar\CYROTLD{}',
0x004E9: r'\cyrchar\cyrotld{}',
0x02002: r'\hspace{0.6em}',
0x02003: r'\hspace{1em}',
0x02004: r'\hspace{0.33em}',
0x02005: r'\hspace{0.25em}',
0x02006: r'\hspace{0.166em}',
0x02007: r'\hphantom{0}',
0x02008: r'\hphantom{,}',
0x02009: r'\hspace{0.167em}',
0x02010: r'-',
0x02013: r'\textendash{}',
0x02014: r'\textemdash{}',
0x02015: r'\rule{1em}{1pt}',
0x02018: r'`',
0x02019: r"'",
0x0201A: r',',
0x0201C: r'\textquotedblleft{}',
0x0201D: r'\textquotedblright{}',
0x0201E: r',,',
0x02020: r'\textdagger{}',
0x02021: r'\textdaggerdbl{}',
0x02022: r'\textbullet{}',
0x02024: r'.',
0x02025: r'..',
0x02026: r'\ldots{}',
0x02030: r'\textperthousand{}',
0x02031: r'\textpertenthousand{}',
0x02039: r'\guilsinglleft{}',
0x0203A: r'\guilsinglright{}',
0x0205F: r'\mkern4mu{}',
0x02060: r'\nolinebreak{}',
0x020A7: r'\ensuremath{\Elzpes}',
0x020AC: r'\mbox{\texteuro}{}',
0x0210A: r'\mathscr{g}',
0x02116: r'\cyrchar\textnumero{}',
0x02122: r'\texttrademark{}',
0x0212B: r'\AA{}',
0x02212: r'-',
0x02254: r':=',
0x02305: r'\barwedge{}',
0x02423: r'\textvisiblespace{}',
0x02460: r'\ding{172}',
0x02461: r'\ding{173}',
0x02462: r'\ding{174}',
0x02463: r'\ding{175}',
0x02464: r'\ding{176}',
0x02465: r'\ding{177}',
0x02466: r'\ding{178}',
0x02467: r'\ding{179}',
0x02468: r'\ding{180}',
0x02469: r'\ding{181}',
0x025A0: r'\ding{110}',
0x025B2: r'\ding{115}',
0x025BC: r'\ding{116}',
0x025C6: r'\ding{117}',
0x025CF: r'\ding{108}',
0x025D7: r'\ding{119}',
0x02605: r'\ding{72}',
0x02606: r'\ding{73}',
0x0260E: r'\ding{37}',
0x0261B: r'\ding{42}',
0x0261E: r'\ding{43}',
0x0263E: r'\rightmoon{}',
0x0263F: r'\mercury{}',
0x02640: r'\venus{}',
0x02642: r'\male{}',
0x02643: r'\jupiter{}',
0x02644: r'\saturn{}',
0x02645: r'\uranus{}',
0x02646: r'\neptune{}',
0x02647: r'\pluto{}',
0x02648: r'\aries{}',
0x02649: r'\taurus{}',
0x0264A: r'\gemini{}',
0x0264B: r'\cancer{}',
0x0264C: r'\leo{}',
0x0264D: r'\virgo{}',
0x0264E: r'\libra{}',
0x0264F: r'\scorpio{}',
0x02650: r'\sagittarius{}',
0x02651: r'\capricornus{}',
0x02652: r'\aquarius{}',
0x02653: r'\pisces{}',
0x02660: r'\ding{171}',
0x02663: r'\ding{168}',
0x02665: r'\ding{170}',
0x02666: r'\ding{169}',
0x02669: r'\quarternote{}',
0x0266A: r'\eighthnote{}',
0x02701: r'\ding{33}',
0x02702: r'\ding{34}',
0x02703: r'\ding{35}',
0x02704: r'\ding{36}',
0x02706: r'\ding{38}',
0x02707: r'\ding{39}',
0x02708: r'\ding{40}',
0x02709: r'\ding{41}',
0x0270C: r'\ding{44}',
0x0270D: r'\ding{45}',
0x0270E: r'\ding{46}',
0x0270F: r'\ding{47}',
0x02710: r'\ding{48}',
0x02711: r'\ding{49}',
0x02712: r'\ding{50}',
0x02713: r'\ding{51}',
0x02714: r'\ding{52}',
0x02715: r'\ding{53}',
0x02716: r'\ding{54}',
0x02717: r'\ding{55}',
0x02718: r'\ding{56}',
0x02719: r'\ding{57}',
0x0271A: r'\ding{58}',
0x0271B: r'\ding{59}',
0x0271C: r'\ding{60}',
0x0271D: r'\ding{61}',
0x0271E: r'\ding{62}',
0x0271F: r'\ding{63}',
0x02720: r'\ding{64}',
0x02721: r'\ding{65}',
0x02722: r'\ding{66}',
0x02723: r'\ding{67}',
0x02724: r'\ding{68}',
0x02725: r'\ding{69}',
0x02726: r'\ding{70}',
0x02727: r'\ding{71}',
0x02729: r'\ding{73}',
0x0272A: r'\ding{74}',
0x0272B: r'\ding{75}',
0x0272C: r'\ding{76}',
0x0272D: r'\ding{77}',
0x0272E: r'\ding{78}',
0x0272F: r'\ding{79}',
0x02730: r'\ding{80}',
0x02731: r'\ding{81}',
0x02732: r'\ding{82}',
0x02733: r'\ding{83}',
0x02734: r'\ding{84}',
0x02735: r'\ding{85}',
0x02736: r'\ding{86}',
0x02737: r'\ding{87}',
0x02738: r'\ding{88}',
0x02739: r'\ding{89}',
0x0273A: r'\ding{90}',
0x0273B: r'\ding{91}',
0x0273C: r'\ding{92}',
0x0273D: r'\ding{93}',
0x0273E: r'\ding{94}',
0x0273F: r'\ding{95}',
0x02740: r'\ding{96}',
0x02741: r'\ding{97}',
0x02742: r'\ding{98}',
0x02743: r'\ding{99}',
0x02744: r'\ding{100}',
0x02745: r'\ding{101}',
0x02746: r'\ding{102}',
0x02747: r'\ding{103}',
0x02748: r'\ding{104}',
0x02749: r'\ding{105}',
0x0274A: r'\ding{106}',
0x0274B: r'\ding{107}',
0x0274D: r'\ding{109}',
0x0274F: r'\ding{111}',
0x02750: r'\ding{112}',
0x02751: r'\ding{113}',
0x02752: r'\ding{114}',
0x02756: r'\ding{118}',
0x02758: r'\ding{120}',
0x02759: r'\ding{121}',
0x0275A: r'\ding{122}',
0x0275B: r'\ding{123}',
0x0275C: r'\ding{124}',
0x0275D: r'\ding{125}',
0x0275E: r'\ding{126}',
0x02761: r'\ding{161}',
0x02762: r'\ding{162}',
0x02763: r'\ding{163}',
0x02764: r'\ding{164}',
0x02765: r'\ding{165}',
0x02766: r'\ding{166}',
0x02767: r'\ding{167}',
0x02776: r'\ding{182}',
0x02777: r'\ding{183}',
0x02778: r'\ding{184}',
0x02779: r'\ding{185}',
0x0277A: r'\ding{186}',
0x0277B: r'\ding{187}',
0x0277C: r'\ding{188}',
0x0277D: r'\ding{189}',
0x0277E: r'\ding{190}',
0x0277F: r'\ding{191}',
0x02780: r'\ding{192}',
0x02781: r'\ding{193}',
0x02782: r'\ding{194}',
0x02783: r'\ding{195}',
0x02784: r'\ding{196}',
0x02785: r'\ding{197}',
0x02786: r'\ding{198}',
0x02787: r'\ding{199}',
0x02788: r'\ding{200}',
0x02789: r'\ding{201}',
0x0278A: r'\ding{202}',
0x0278B: r'\ding{203}',
0x0278C: r'\ding{204}',
0x0278D: r'\ding{205}',
0x0278E: r'\ding{206}',
0x0278F: r'\ding{207}',
0x02790: r'\ding{208}',
0x02791: r'\ding{209}',
0x02792: r'\ding{210}',
0x02793: r'\ding{211}',
0x02794: r'\ding{212}',
0x02798: r'\ding{216}',
0x02799: r'\ding{217}',
0x0279A: r'\ding{218}',
0x0279B: r'\ding{219}',
0x0279C: r'\ding{220}',
0x0279D: r'\ding{221}',
0x0279E: r'\ding{222}',
0x0279F: r'\ding{223}',
0x027A0: r'\ding{224}',
0x027A1: r'\ding{225}',
0x027A2: r'\ding{226}',
0x027A3: r'\ding{227}',
0x027A4: r'\ding{228}',
0x027A5: r'\ding{229}',
0x027A6: r'\ding{230}',
0x027A7: r'\ding{231}',
0x027A8: r'\ding{232}',
0x027A9: r'\ding{233}',
0x027AA: r'\ding{234}',
0x027AB: r'\ding{235}',
0x027AC: r'\ding{236}',
0x027AD: r'\ding{237}',
0x027AE: r'\ding{238}',
0x027AF: r'\ding{239}',
0x027B1: r'\ding{241}',
0x027B2: r'\ding{242}',
0x027B3: r'\ding{243}',
0x027B4: r'\ding{244}',
0x027B5: r'\ding{245}',
0x027B6: r'\ding{246}',
0x027B7: r'\ding{247}',
0x027B8: r'\ding{248}',
0x027B9: r'\ding{249}',
0x027BA: r'\ding{250}',
0x027BB: r'\ding{251}',
0x027BC: r'\ding{252}',
0x027BD: r'\ding{253}',
0x027BE: r'\ding{254}',
0x0FB00: r'ff',
0x0FB01: r'fi',
0x0FB02: r'fl',
0x0FB03: r'ffi',
0x0FB04: r'ffl',
0x1D6B9: r'\mathbf{\vartheta}',
0x1D6DD: r'\mathbf{\vartheta}',
0x1D6DE: r'\mathbf{\varkappa}',
0x1D6DF: r'\mathbf{\phi}',
0x1D6E0: r'\mathbf{\varrho}',
0x1D6E1: r'\mathbf{\varpi}',
0x1D6F3: r'\mathsl{\vartheta}',
0x1D717: r'\mathsl{\vartheta}',
0x1D718: r'\mathsl{\varkappa}',
0x1D719: r'\mathsl{\phi}',
0x1D71A: r'\mathsl{\varrho}',
0x1D71B: r'\mathsl{\varpi}',
0x1D72D: r'\mathbit{O}',
0x1D751: r'\mathbit{\vartheta}',
0x1D752: r'\mathbit{\varkappa}',
0x1D753: r'\mathbit{\phi}',
0x1D754: r'\mathbit{\varrho}',
0x1D755: r'\mathbit{\varpi}',
0x1D767: r'\mathsfbf{\vartheta}',
0x1D78B: r'\mathsfbf{\vartheta}',
0x1D78C: r'\mathsfbf{\varkappa}',
0x1D78D: r'\mathsfbf{\phi}',
0x1D78E: r'\mathsfbf{\varrho}',
0x1D78F: r'\mathsfbf{\varpi}',
0x1D7A1: r'\mathsfbfsl{\vartheta}',
0x1D7C5: r'\mathsfbfsl{\vartheta}',
0x1D7C6: r'\mathsfbfsl{\varkappa}',
0x1D7C7: r'\mathsfbfsl{\phi}',
0x1D7C8: r'\mathsfbfsl{\varrho}',
0x1D7C9: r'\mathsfbfsl{\varpi}',
}

# keymap contains substitutions to try to fall back on normal 7-bit ASCII
# characters
keymap = {
0x000A0: r'',
0x000AD: r'',
0x0007E: r'',
0x000A1: r'',
0x000A2: r'',
0x000A3: r'',
0x000A4: r'',
0x000A5: r'',
0x000A6: r'',
0x000A7: r'',
0x000A8: r'',
0x000A9: r'',
0x000AA: r'',
0x000AB: r'',
0x000AE: r'',
0x000AF: r'',
0x000B0: r'',
0x000B4: r'',
0x000B6: r'',
0x000B8: r'',
0x000BA: r'',
0x000BB: r'',
0x000BC: r'',
0x000BD: r'',
0x000BE: r'',
0x000BF: r'',
0x000C0: r'A',
0x000C1: r"A",
0x000C2: r'A',
0x000C3: r'A',
0x000C4: r'A',
0x000C5: r'A',
0x000C6: r'Ae',
0x000C7: r'C',
0x000C8: r'E',
0x000C9: r"E",
0x000CA: r'E',
0x000CB: r'E',
0x000CC: r'I',
0x000CD: r"I",
0x000CE: r'I',
0x000CF: r'I',
0x000D0: r'', # TODO was \DH
0x000D1: r'N',
0x000D2: r'O',
0x000D3: r"O",
0x000D4: r'O',
0x000D5: r'O',
0x000D6: r'O',
0x000D7: r'x',
0x000D8: r'O',
0x000D9: r'U',
0x000DA: r"U",
0x000DB: r'U',
0x000DC: r'U',
0x000DD: r"Y",
0x000DE: r'', # TODO was \TH
0x000DF: r'ss',
0x000E0: r'a',
0x000E1: r"a",
0x000E2: r'a',
0x000E3: r'a',
0x000E4: r'a',
0x000E5: r'a',
0x000E6: r'ae',
0x000E7: r'c',
0x000E8: r'e',
0x000E9: r"e",
0x000EA: r'e',
0x000EB: r'e',
0x000EC: r'i',
0x000ED: r"i",
0x000EE: r'i',
0x000EF: r'i',
0x000F0: r'', # TODO was \dh
0x000F1: r'n',
0x000F2: r'o',
0x000F3: r"o",
0x000F4: r'o',
0x000F5: r'o',
0x000F6: r'o',
0x000F8: r'o',
0x000F9: r'u',
0x000FA: r"u",
0x000FB: r'u',
0x000FC: r'u',
0x000FD: r"y",
0x000FE: r'', # TODO was \th
0x000FF: r'y',
0x00100: r'A',
0x00101: r'a',
0x00102: r'A',
0x00103: r'a',
0x00104: r'A',
0x00105: r'a',
0x00106: r"C",
0x00107: r"c",
0x00108: r'C',
0x00109: r'c',
0x0010A: r'C',
0x0010B: r'c',
0x0010C: r'C',
0x0010D: r'c',
0x0010E: r'D',
0x0010F: r'd',
0x00112: r'E',
0x00113: r'e',
0x00114: r'E',
0x00115: r'e',
0x00116: r'E',
0x00117: r'e',
0x00118: r'E', 
0x00119: r'e',
0x0011A: r'E',
0x0011B: r'e',
0x0011C: r'G',
0x0011D: r'g',
0x0011E: r'G',
0x0011F: r'g',
0x00120: r'G',
0x00121: r'g',
0x00122: r'G',
0x00123: r'g',
0x00124: r'H',
0x00125: r'h',
0x00128: r'I',
0x00129: r'i',
0x0012A: r'I',
0x0012B: r'i',
0x0012C: r'I',
0x0012D: r'i',
0x0012E: r'I',
0x0012F: r'i',
0x00130: r'I',
0x00131: r'i',
0x00132: r'IJ',
0x00133: r'ij',
0x00134: r'J',
0x00135: r'j',
0x00136: r'K',
0x00137: r'k',
0x00139: r"L",
0x0013A: r"l",
0x0013B: r'L',
0x0013C: r'l',
0x0013D: r'L',
0x0013E: r'l',
0x00141: r'L',
0x00142: r'l',
0x00143: r"N",
0x00144: r"n",
0x00145: r'N',
0x00146: r'n',
0x00147: r'N',
0x00148: r'n',
0x00149: r"n",
0x0014A: r'NG',
0x0014B: r'ng',
0x0014C: r'O',
0x0014D: r'o',
0x0014E: r'O',
0x0014F: r'o',
0x00150: r'O',
0x00151: r'o',
0x00152: r'OE',
0x00153: r'oe',
0x00154: r"R",
0x00155: r"r",
0x00156: r'R',
0x00157: r'r',
0x00158: r'R',
0x00159: r'r',
0x0015A: r"S",
0x0015B: r"s",
0x0015C: r'S',
0x0015D: r's',
0x0015E: r'S',
0x0015F: r's',
0x00160: r'S',
0x00161: r's',
0x00162: r'T',
0x00163: r't',
0x00164: r'T',
0x00165: r't',
0x00168: r'U',
0x00169: r'u',
0x0016A: r'U',
0x0016B: r'u',
0x0016C: r'U',
0x0016D: r'u',
0x0016E: r'U',
0x0016F: r'u',
0x00170: r'U',
0x00171: r'u',
0x00172: r'U',
0x00173: r'u',
0x00174: r'W',
0x00175: r'w',
0x00176: r'Y',
0x00177: r'y',
0x00178: r'Y',
0x00179: r"Z",
0x0017A: r"z",
0x0017B: r'Z',
0x0017C: r'z',
0x0017D: r'Z',
0x0017E: r'z',
0x001F5: r"g",
0x00261: r'g',
0x00386: r"A",
0x00388: r"E",
0x00389: r"H",
0x0038A: r"I",
0x0038C: r"O",
0x003AC: r"a",
0x003CC: r"o",
0x0FB00: r'ff',
0x0FB01: r'fi',
0x0FB02: r'fl',
0x0FB03: r'ffi',
0x0FB04: r'ffl',
}

def clean(x):
    """Converts string into LaTeX-equivalent text"""

    y = ""
    for char in x:
        if textescmap.has_key(char):
            y = y + textescmap[char]  
            continue
        
        if textmap.has_key(ord(char)):
            y = y + textmap[ord(char)]
            continue
        
        if ord(char) > 127:
            try:
                # use the ^^XX form
                bytes = char.encode('ascii')
                for by in bytes:
                    y = y + '^^%02x' % ord(by)
                continue
            except Exception, e:
                #print "Exception in ^^XX attempt: %s" % e
                pass

        # last resort -- must \usepackage{ucs}
        if ord(char) > 127:
            y = y + "\\unichar{" + str(ord(char)) + "}"
            continue

        y = y + char

    return y

def cleankey(x):
    """Strips accents and special chars, leaving only A-Z, a-z, and 0-9"""
    y = ""
    for char in x:
        if keymap.has_key(ord(char)):
            y = y + keymap[ord(char)]
        elif ord(char) in range(65, 91) or ord(char) in range(97, 123) or ord(char) in range(48, 58):   # A-Z, a-z, and 0-9
            y = y + char

    return y


def valid_key(bib_dict, key):
    # if the bib_dict is empty, return the key
    if bib_dict.keys() == []:
        return key

    # if there's no year in the key, add one
    has_year = False
    for char in key:
        if ord(char) in range(ord('0'), ord('9')+1):
            has_year = True
            break
    if not has_year:
        key = key + "0000"
    
    # add all similar keys to the existing_keys list
    existing_keys = []
    for k in bib_dict.keys():
        if k is None:
            continue
           
        if k.lower().startswith(key.lower()):
            existing_keys.append(k)

    # find the latest key appendix
    max_postfix = ''
    existing_keys.sort()
    for k in existing_keys:
        key_parts = re.split(r'[0-9]+', k)
        if len(key_parts[-1]) > len(max_postfix):
            max_postfix = key_parts[-1]
        elif len(key_parts[-1]) == len(max_postfix):
            if key_parts[-1] > max_postfix:
                max_postfix = key_parts[-1]

    # FIXME what if there's no date?  (re: repeated author names)
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
        #print "didn't find ordinal:", x
        return x


def getauthorslist(author_fl, other_authors):
    if other_authors == '':
        return author_fl
    else:
        authors_list = [author_fl]
        authors_list.extend(other_authors.split(", "))
        return " and ".join(authors_list)


def main():
    # Send http headers
    print "Content-Type: text/plain"
    print

    # Process the form data
    form = cgi.FieldStorage()

    latex = True
    #latex = form["generate_latex"] # FIXME how can we dump two files? (.bib and .tex)

    fileitem = form["lt_file"]
    if fileitem.filename:
        # strip leading path from file name to avoid directory traversal attacks
        timestamp = str(datetime.datetime.utcnow()).replace(" ", "_")
        #fn = os.path.basename(fileitem.filename) + "_" + timestamp
        fn = "LibraryThing_" + timestamp + ".xls"
        input_file = os.path.join('uploads', fn)
        open('uploads/' + fn, 'wb').write(fileitem.file.read())
        bookdata = codecs.open(input_file, 'rb', 'utf-16')
        lines = bookdata.readlines()
        bibtex_file = file(os.path.join("uploads", "LibraryThing_" + timestamp + ".bib"), 'w')
    else:
        print "Error: File isn't valid."
        return

    #bibtex_file = file("LibraryThing.bib", 'w')
    latex_file = file(os.path.join("uploads", "LibraryThing_" + timestamp + ".tex"), 'w')
    latex_file.write("""\\documentclass{article}
\\usepackage{apacite}
\\usepackage{ucs}  % unicode support
\\title{Test of the \\texttt{LibraryThing.bib} file}
\\begin{document}
\\begin{itemize}
""")

    #bibtex_file.write("line\n")

    bib_dict = { }
    linenum = -1 
    for l in lines:
        linenum = linenum + 1
        if 0 == linenum:        # ignore the header line
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
        author_fl     = clean(line[2])  # author, first-last
        author_lf     = clean(line[3])  # author, last-first
        other_authors = clean(line[4])  # other authers
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
        comments      = clean(line[24]) # comments
        encoding      = line[25] # encoding

        # FIXME Check language -- if it's something we can't handle yet, skip it for now
        #if lang1 != "English":
        #    continue

        # Authors
        author = getauthorslist(author_fl, other_authors)
        
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
        if len(publication_info) > 1:
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
        #note = comments    # FIXME comment fields contain all sorts of crazy stuff
        note = ""

        if isbn != '' and isbn != '[]':
            #otherinfo = "ISBN " + isbn[1:-1]
            isbn = isbn[1:-1]
        else:
            isbn = ""

        # Calculate the key (usually author's last name + 4-digit year)
        if author == '':
            if editor == '':
                #print "Warning: %s has no author or editor!" % (title)
                key = "UnknownAuthor" + date
            else:
                key = editor + date
        else:
            #key = author_lf.split(',')[0] + date
            key = cleankey(line[3].split(',')[0]) + date

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
        }


        print "@BOOK{%s," % key
        if len(author) > 0: print "\tauthor = {%s}," % author
        #print "\teditor = {%s}," % editor
        if len(title) > 0: print "\ttitle = {%s}," % title
        if len(publisher) > 0: print "\tpublisher = {%s}," % publisher
        if len(year) > 0: print "\tyear = {%s}," % year
        #print "\taddress = {%s}," % address
        if len(edition) > 0: print "\tedition = {%s}," % edition
        #print "\tvolume = {%s}," % volume
        #print "\tnumber = {%s}," % number
        #print "\tseries = {%s}," % series
        #print "\tmonth = {%s}," % month
        #print "\tnote = {%s}," % note
        if len(isbn) > 0: print "\tisbn = {%s}" % isbn
        #print "\totherinfo = {%s}" % otherinfo
        print "}\n"

        bibtex_file.write("@BOOK{%s,\n" % key)
        bibtex_file.write("\tauthor = {%s},\n" % author)
        bibtex_file.write("\teditor = {%s},\n" % editor)
        bibtex_file.write("\ttitle = {%s},\n" % title)
        bibtex_file.write("\tpublisher = {%s},\n" % publisher)
        bibtex_file.write("\tyear = {%s},\n" % year)
        bibtex_file.write("\taddress = {%s},\n" % address)
        bibtex_file.write("\tedition = {%s},\n" % edition)
        bibtex_file.write("\tvolume = {%s},\n" % volume)
        bibtex_file.write("\tnumber = {%s},\n" % number)
        bibtex_file.write("\tseries = {%s},\n" % series)
        bibtex_file.write("\tmonth = {%s},\n" % month)
        bibtex_file.write("\tnote = {%s},\n" % note)
        bibtex_file.write("\tisbn = {%s}\n" % isbn)
        #bibtex_file.write("\totherinfo = {%s}\n" % otherinfo)
        bibtex_file.write("}\n\n")

        latex_file.write("\\item %s \\cite{%s}\n" % (title, key))

    # Finished with the loop now

    # Close the LaTeX file
    latex_file.write("""
\\end{itemize}
\n\n
\\bibliographystyle{apacite}
\\bibliography{LibraryThing}
\\end{document}
""")
    latex_file.close()
    bibtex_file.close()




if __name__ == "__main__":
    main()

