goxgui - forked by genBTC
======

About
-----

goxgui is a Qt front end for [prof7bit's goxtool](http://prof7bit.github.io/goxtool/). This is what it looks like:

![Screenshot](https://raw.github.com/genbtc/goxgui/master/genBTCScreenshot_3.png)

Features
--------
* Stop-Loss market sell orders (new tab)
* Display User Orders (new tab)
* Display asks / bids (Order Book tab)
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
