#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This library is written by Juhani "nortti" Haverinen. Version 2
# It defines functions for converting from and to the character encoding of lm1125
# encode() and decode() have similar but not identical interface to python codecs
# To best of my knowledge both Python 3 and Python 2 work

# This is free and unencumbered software released into the public domain.
# 
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
# 
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
# 
# For more information, please refer to [http://unlicense.org]

# Encoding used appears to be a variant of JIS X 0201
# Same as JIS X 0201: 02 - 03, 06 - 07, 0A - 0B, 0E - 7D, 80 - DF
# Differences from JIS X 0201:
# 00, 01, 08, 09
# ▄
# 04, 05, 0C, 0D, FF
# █
# 7E - 7F
# → ←
# E0 - FE
# α ä β ε µ σ ρ ą √ ⁻¹ ị ˣ ¢ Ⱡ ñ ö ḅ ḍ θ ∞ Ω ü Σ π x̄ ų 千 万 円 ÷

# py2 compatibility
from __future__ import unicode_literals
from __future__ import print_function
import sys

if sys.version_info.major < 3:
	bytechr = chr
	byteord = ord
	as_byte = byteord
	input = lambda prompt='': raw_input(prompt).decode('utf-8')
else:
	bytechr = lambda x: bytes([x])
	byteord = lambda x: x[0]
	as_byte = lambda x: x

# Set up translation table from charset to unicode (outside of JIS X 0201)
charset_to_unicode = {}
# Two block characters
for i in [0, 1, 8, 9]:
	charset_to_unicode[i] = '\u2584'
for i in [4, 5, 12, 13, 255]:
	charset_to_unicode[i] = '\u2588'
# Arrows
charset_to_unicode[126] = '←'
charset_to_unicode[127] = '→'
# the range E0 - FE
for codepoint, unicode in zip(range(224, 255), 'α ä β ε µ σ ρ ą √ ⁻¹ ị ˣ ¢ Ⱡ ñ ö ḅ ḍ θ ∞ Ω ü Σ π x̄ ų 千 万 円 ÷'.split()):
	charset_to_unicode[codepoint] = unicode
# Define A0 to be U+00 as otherwise that one codepoint would fall outside of decoding coverage
charset_to_unicode[0xa0] = '\u0000'

# Set up translation table from unicode to charset (outside of JIS X 0201)
unicode_to_charset = {}
# Set up reverse correspondence for all charset→unicode ones
for codepoint in charset_to_unicode:
	unicode = charset_to_unicode[codepoint]
	unicode_to_charset[unicode] = codepoint

# Here you can "alias" a character, e.g. £ should be encoded as Ⱡ
# If a character is not a part of the charset and an alias is not set, it is represented by a replacement character
default_aliases = {
	# Same character, encoded differently
	'ä': 'ä', 'ö': 'ö', 'ü': 'ü', 'ị': 'ị',
	# Similar character
	'£': 'Ⱡ', 'n̄': 'ñ', '·': '･', '∣': '|', '⟨': '<', '⟩': '>',
	# Fullwidth → halfwidth katakana
	'ア': 'ｱ', 'イ': 'ｲ', 'ウ': 'ｳ', 'エ': 'ｴ', 'オ': 'ｵ', 'ヴ': 'ｳﾞ',
	'カ': 'ｶ', 'キ': 'ｷ', 'ク': 'ｸ', 'ケ': 'ｹ', 'コ': 'ｺ', 'ガ': 'ｶﾞ', 'ギ': 'ｷﾞ', 'グ': 'ｸﾞ', 'ゲ': 'ｹﾞ', 'ゴ': 'ｺﾞ',
	'サ': 'ｻ', 'シ': 'ｼ', 'ス': 'ｽ', 'セ': 'ｾ', 'ソ': 'ｿ', 'ザ': 'ｻﾞ', 'ジ': 'ｼﾞ', 'ズ': 'ｽﾞ', 'ゼ': 'ｾﾞ', 'ゾ': 'ｿﾞ',
	'タ': 'ﾀ', 'チ': 'ﾁ', 'ツ': 'ﾂ', 'テ': 'ﾃ', 'ト': 'ﾄ', 'ダ': 'ﾀﾞ', 'ヂ': 'ﾁﾞ', 'ヅ': 'ﾂﾞ', 'デ': 'ﾃﾞ', 'ド': 'ﾄﾞ',
	'ナ': 'ﾅ', 'ニ': 'ﾆ', 'ヌ': 'ﾇ', 'ネ': 'ﾈ', 'ノ': 'ﾉ',
	'ハ': 'ﾊ', 'ヒ': 'ﾋ', 'フ': 'ﾌ', 'ヘ': 'ﾍ', 'ホ': 'ﾎ', 'バ': 'ﾊﾞ', 'ビ': 'ﾋﾞ', 'ブ': 'ﾌﾞ', 'ベ': 'ﾍﾞ', 'ボ': 'ﾎﾞ', 'パ': 'ﾊﾟ', 'ピ': 'ﾋﾟ', 'プ': 'ﾌﾟ', 'ペ': 'ﾍﾟ', 'ポ': 'ﾎﾟ',
	'マ': 'ﾏ', 'ミ': 'ﾐ', 'ム': 'ﾑ', 'メ': 'ﾒ', 'モ': 'ﾓ',
	'ラ': 'ﾗ', 'リ': 'ﾘ', 'ル': 'ﾙ', 'レ': 'ﾚ', 'ロ': 'ﾛ',
	'ワ': 'ﾜ', 'ヲ': 'ｦ', 'ン': 'ﾝ', 'ヷ': 'ﾜﾞ', 'ヺ': 'ｦﾞ',
	'ァ': 'ｧ', 'ィ': 'ｨ', 'ゥ': 'ｩ', 'ェ': 'ｪ', 'ォ': 'ｫ', 'ャ': 'ｬ', 'ュ': 'ｭ', 'ョ': 'ｮ', 'ッ': 'ｯ',
	'ー': 'ｰ', '。': '｡', '「': '｢', '」': '｣', '、': '､', '・': '･',
}

# Define the default replacement character
default_replacement_character = 0

def prefix_matches(text, option):
	return len(text) >= len(option) and text[:len(option)] == option

def in_range(value, value_range):
	start, end = value_range
	return value in range(start, end+1)

def in_ranges(value, value_ranges):
	return any(map(lambda value_range: in_range(value, value_range), value_ranges))

def jis_encodable(unicode):
	codepoint = ord(unicode)
	# Correspond to JIS X 0201 5C, A1 - DF
	return in_ranges(codepoint, [(0xa5, 0xa5), (0xff61, 0xff9f)])

def identity_encodable(unicode):
	codepoint = ord(unicode)
	# Can be mapped into JIS X 0201 by doing byte = codepoint
	return in_ranges(codepoint, [(0x02, 0x03), (0x06, 0x07), (0x0a, 0x0b), (0x0e, 0x5b), (0x5d, 0x7d), (0x80, 0x9F)])

def jis_decodable(byte):
	# Correspond to U+A5, U+FF61 - U+FF9F
	return in_ranges(byte, [(0x5c, 0x5c), (0xa1, 0xdf)])

def identity_decodable(byte):
	# Can be mapped into unicode by doing codepoint = byte
	return in_ranges(byte, [(0x02, 0x03), (0x06, 0x07), (0x0a, 0x0b), (0x0e, 0x5b), (0x5d, 0x7d), (0x80, 0x9F)])

def encode(text, aliases = default_aliases, replacement_character = default_replacement_character):
	""" When passed either an unicode string or utf-8 bytestring, converts to the lm1125 charset.
	If a character cannot be encoded, replacement_character is used in its place.
	`aliases` is a dictionary of { 'unicode string': 'replacement unicode string' }, telling the encoder how to replace characters / sequences it cannot encode.
	`replacement_character` is an integer in the range 0 - 255, representing the byte value of the choosen character in lm1125 charset.
	The default values of `aliases` and `replacement_character` are accessible as default_aliases and default_replacement_character """

	# Ensure we have Unicode string
	if type(text) != type(''):
		text = text.decode('utf-8')

	encoded = b''

	index = 0
	length = len(text)
	while index < length:
		character = text[index] # If it's a nice one-to-one correspondence

		if identity_encodable(character):
			encoded += bytechr(ord(character))
			index += 1
		elif jis_encodable(character):
			encoded += character.encode('shift-jis')
			index += 1
		else:
			# Now we have to go into lookup tables
			matched = False

			# Check to see if in the table of characters different between charset and JIS X 0201
			for unicode in unicode_to_charset:
				if prefix_matches(text[index:], unicode):
					encoded += bytechr(unicode_to_charset[unicode])
					index += len(unicode)
					matched = True
					break

			if matched: continue # Already encoded this, let's move to next one

			# Check to see if in the table of aliases
			for unicode in aliases:
				if prefix_matches(text[index:], unicode):
					# Recursively call self on the unicode defined in the aliases table
					encoded += encode(aliases[unicode], aliases = aliases, replacement_character = replacement_character)
					index += len(unicode)
					matched = True
					break

			if not matched:
				# We simply cannot represent this character, use let's use the replacement character and move to next
				encoded += bytechr(default_replacement_character)
				index += 1
	
	return encoded

def decode(text):
	""" When passed a bytestring in lm1125 charset, converts to Unicode string.
	Conversion to Unicode is not round-trip safe. """
	decoded = ''

	index = 0
	length = len(text)
	while index < length:
		character = as_byte(text[index])

		if identity_decodable(character):
			decoded += chr(character)
			index += 1
		elif jis_decodable(character):
			decoded += bytechr(character).decode('shift-jis')
			index += 1
		else:
			matched = False

			# See if in the table of characters different between charset and JIS X 0201
			for byte in charset_to_unicode:
				if byte == character:
					decoded += charset_to_unicode[byte]
					index += 1
					matched = True
					break

			if not matched:
				# All 256 characters should have a correspondence
				assert(not 'Unreachable')
	
	return decoded

if __name__ == '__main__':
	line = input()
	print(decode(encode(line)))
