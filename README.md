**RansPy**
======

What is RansPy?
---------------

For my Master of Science in Digital Security, I developed a ransomware in Python. I found RansPy by **Marcos Valle** (https://github.com/marcosValle/RansPy) which helped me a lot on the encryption / decryption part.

How RansPy works?
-----------------

RansPy encrypts all files in a directory defined in the Python script into AES-128. It adds a ".encrypted" extension to the encrypted files.

To decrypt the files, a decryption code must be retrieved from a website developed in HTML, CSS, JavaScript and PHP. Once the decryption code is received, simply enter it in RansPy. The files then lose the extension ".encrypted" and are decrypted.

Details
-------

At the launch of RansPy, two keys are generated, encrypted in base64 and sent to the database "ranspy":
- "software_key" as the application identifier.
- "decrypt_key" as the decryption key.

When the target enters its software_key on the website, it obtains the decrypt_key associated with its software_key.

Of course, we can imagine all kinds of system to replace the existing one because it is currently free.

Information
-----------

 - The script is in Python 2.7
 - I used Tkinter for the GUI
 - The default target directory is C:\RansPy (Windows).
 - The decryption code is obtained free of charge.
 - To create a ".exe" for Windows, I recommend installing PyInstaller (https://www.pyinstaller.org/).

Project files
-------------

 **database**

 - ranspy.sql
	 - ranspy_keys
		 - software_key -> char(32)
		 - decrypt_key -> char(32)
		 - date -> datetime

**python**

 - ranspy.exe
 - ranspy.py

**website**

 - css
	 - fonts
		 - GearsOfPeace.eot
		 - GearsOfPeace.svg
		 - GearsOfPeace.ttf
		 - GearsOfPeace.woff
	 - style.css
 - img
	 - logo-ranspy.png
	 - logo-ranspy-ok.png
 - js
	 - jquery-min.js
 - php
	 - get_decrypt_code.php
 - index.php

Disclaimer
----------

The use of this software is dangerous and you are responsible for the compatibility of this software with your software and hardware. You are also responsible for protecting your equipment and data. I will not be liable for any damages you may suffer as a result of using, modifying or distributing this software.
