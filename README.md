goxgui - forked by genBTC (updated 5/8/2013)
======

About
-----

goxgui is a Qt front end for [prof7bit's goxtool](http://prof7bit.github.io/goxtool/). This is what it looks like:

![Screenshot](https://raw.github.com/genbtc/goxgui/master/genBTCScreenshot_4.png)

Features
--------
* Create Stop-Loss market sell orders (new tab)
* Display User Orders (new tab)
* Display asks / bids (Order Book tab)
* Ticker in Title bar (and new Ticker Tab with auto-refresh)
* Display MtGox account balance (USD/BTC)
* Display MtGox lag
* Place and cancel orders (USD)


Prerequisites
-------------

I have tested the application on **OSX 10.7.5** and **Windows XP** within the following confguration. Other setups may or may not work.

* Python 2.7.3
* Qt 4.8.2
* PyQt (matching the above Python / Qt versions)
* pycrypto 2.6

goxtool will be downloaded with goxgui, so you don't need to install it manually.

Installation from Source
------------

Please note: **you must make sure all prerequisites above are installed first **, otherwise the application will not work.

    git clone --recursive git://github.com/genbtc/goxgui.git

or download the zip file and extract the whole structure to a new directory.

Then run the program by:

    cd goxgui/run
    chmod 755 ./start_linux.sh
    ./start_linux.sh             # not on linux? leave out the above line and run ./start_mac.sh or start_win.bat

Windows EXE
----------------
The goxgui.exe is a pre-compiled binary verson, and should work fine (although there is no icon...)
[Download Link](https://raw.github.com/genbtc/goxgui/master/goxgui.exe)


API Key/Secret & Password
--------------------------
The API key and Secret, are encrypted in the .ini file. Previously the password they were encrypted with was hardcoded, not user-choosable and I found this odd (security hole). So I cobbled together the method that you see in my forked version, therefore the steps to use this functionality are somewhat sub-par in terms of intuitiveness, so heres the instructions.

1) Download the fork from https://github.com/genbtc/goxgui

2) The program will generate a new blank config file on first run. (Don't try to import the old one)

3) Click the "Authentication" Tab, enter your API Key and Secret

4) Click the "Password" Tab, enter your Password of your own choosing.

5) Go BACK to the "Authentication" Tab, and hit Apply.

6) The program will encrypt the API Key/Secret and store it in the INI file.

7) Each Next time you want to open up the program, you will have to click the password tab, enter your Password, and hit "Decrypt".

I Have just implemented a "lazy-version" of this. Once You have done initial Steps 1-6 above, You can edit the "goxtool.ini" file and add the following, replacing XXXXX with your chosen password:

[goxgui]

password = XXXXXXXXXXXX


This will store your password, and auto-login everytime you launch it next time.


Requests
--------

Bugs and feature requests can be posted in [the goxgui thread on bitcointalk.org](https://bitcointalk.org/index.php?topic=176489.0).

Donations
---------

1QAbFdV6KDqMsFG9bjmeeBYCQzymXpsifc (sebastianhabery)
13iDBNombaN4HoXsqcM3smuKHTum3LrBx6 (genBTC)


Disclaimer
----------

This software is provided “as is," and you use the software at your own risk. 
The menu Tools/Options/Settings is non-functional, and is to be implemented at a later date.