lm1125_charset
==============

Synopsis
--------
This library defines functions for converting from and to the character encoding of lm1125. It works on both Python 3 and Python 2.

API Reference
-------------

	lm1125_charset.encode(text, [aliases], [replacement_character]) → encoded
Encodes either an unicode string or a utf-8 bytestring in the lm1125 character encoding. See help(lm1125_charset.encode) for more details.

	lm1125_charset.decode(text) → decoded
Decodes a bytestring in lm1125 character encoding into an unicode string. See help(lm1125_charset.decode) for more details.

	lm1125_charset.default_aliases
A dictionary of the default character aliases passed to `lm1125_charset.encode()`. Should not be edited. See help(lm1125_charset.encode) for more details about aliases.

	lm1125_charset.default_replacement_character
An integer holding the byte value of the default replacement character passed to `lm1125_charset.encode()`. Should not be edited. See help(lm1125_charset.encode) for more details about replacement character.

Example code
------------
See lcd_framebuffer.py

lcd_framebuffer
===============

Synopsis
--------
This library defines a lcd framebuffer object that can be used to more nicely write data to the LCD screen.

API Reference
-------------

	lcd_framebuffer.LCD_framebuffer(write, width, height) → <LCD_framebuffer object>
Returns a LCD_framebuffer object with write-function `write`, and defined width and height.
The write-function should accept a lm1125 character set string as its first argument and integer determining the row to write as its second argument.

	LCD_framebuffer.dimensions() → (width, height)
Get the dimensions of framebuffer.

	LCD_framebuffer.get_cursor() → (row, column)
Get the current position of cursor in the framebuffer

	LCD_framebuffer.set_cursor(row, column)
Set the position of cursor. Raises an IndexError if the position is not possible.

	LCD_framebuffer.clear_screen()
Empties the framebuffer.

	LCD_framebuffer.write(text)
Writes unicode string at current cursor position.

	LCD_framebuffer.sync()
Updates the screen to use the framebuffer's contents.
