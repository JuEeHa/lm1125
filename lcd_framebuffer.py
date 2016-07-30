#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This library is written by Juhani "nortti" Haverinen. Version 1
# It defines a framebuffer object for more convenient usage of an LCD screen

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


import lm1125_charset

import sys

if sys.version_info.major < 3:
	as_integer = ord
	input = lambda prompt = '': raw_input(prompt).decode('utf-8')
	to_bytestring = lambda list: ''.join(map(chr, list))
else:
	as_integer = lambda x: x
	to_bytestring = lambda list: bytes(list)

class LCD_framebuffer:
	def __init__(self, write, width, height):
		self.lcd_write = write

		self.width = width
		self.height = height
		self.cursor_row = 0
		self.cursor_column = 0
		
		self.clear_screen()
		self.sync()
	
	def clear_screen(self):
		self.framebuffer = [[0x20 for i in range(self.width)] for i in range(self.height)]
	
	def sync(self):
		# Iterate through every line and print to screen
		for row in range(self.height):
			self.lcd_write(to_bytestring(self.framebuffer[row]), row)

	def dimensions(self):
		return (self.width, self.height)
	
	def get_cursor(self):
		return (self.cursor_row, self.cursor_column)
	
	def set_cursor(self, row, column):
		if row in range(self.height) and column in range(self.width):
			self.cursor_row = row
			self.cursor_column = column
		else:
			raise IndexError('Cursor outside of screen')
	
	def __write_character(self, character):
		# NOTE: Character needs to be in lm1125 encoding
		if character == 10: # \n
			# Special handling for newline:
			self.cursor_row += 1
			self.cursor_column = 0
		else:
			# Write character into the framebuffer
			self.framebuffer[self.cursor_row][self.cursor_column] = character
			# Advance the cursor
			self.cursor_column += 1
		
		# If cursor went past end of the line, move to new line
		if self.cursor_column >= self.width:
			self.cursor_row += self.cursor_column // self.width
			self.cursor_column = self.cursor_column % self.width
		
		# If cursor went past end of screen, scroll the screen
		if self.cursor_row >= self.height:
			# Last line is self.height - 1, so the line after that (where need scroll_amount = 1), is self.height
			scroll_amount = self.cursor_row - self.height + 1
			
			for row in range(self.height):
				if row + scroll_amount < self.height:
					# There is a valid row to copy on top of this
					self.framebuffer[row] = self.framebuffer[row + scroll_amount]
				else:
					# No rows to copy, use an empty one
					self.framebuffer[row] = [0x20 for i in range(self.width)]
			
			self.cursor_row -= scroll_amount
	
	def write(self, string):
		string_encoded = lm1125_charset.encode(string)
		for character in string_encoded:
			self.__write_character(as_integer(character))

if __name__ == '__main__':
	import lcd
	# Assumes `lcd.write(text, row)` takes a bytestring in the lm1125 character encoding and writes it on the display in the specified row and `lcd.width()` and `lcd.height()` return its dimensions.
	framebuffer = LCD_framebuffer(write = lcd.write, height = lcd.height(), width = lcd.width())

	while True:
		try:
			command = input('> ')
		except EOFError:
			break

		if command == 'clear':
			framebuffer.clear_screen()
			framebuffer.sync()

		elif command == 'cursor':
			row, column = framebuffer.get_cursor()
			print('Row: %i Column: %i' % (row, column))

		elif command == 'dimensions':
			width, height = framebuffer.dimensions()
			print('Rows: %i Columns: %i' % (height, width))

		elif command == 'help':
			print(' clear      - clear the screen')
			print(' cursor     - get cursor position')
			print(' dimensions - print the dimensions of the screen')
			print(' help       - print this message')
			print(' newline    - print a newline to screen')
			print(' move       - move cursor')
			print(' text       - print text to screen')
			print(' ^D         - exit')
		
		elif command == 'move':
			row = int(input('row: '))
			column = int(input('column: '))

			try:
				framebuffer.set_cursor(row, column)
			except IndexError:
				print('Given cursor position outside of range')

		elif command == 'newline':
			framebuffer.write('\n')
			framebuffer.sync()

		elif command == 'text':
			text = input('text: ')
			framebuffer.write(text)
			framebuffer.sync()

		else:
			print('Unrecognised command "%s"' % command)
