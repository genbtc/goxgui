goxgui - forked by genBTC (updated 5/8/2013)
======

About
-----

goxgui is a Qt front end for [prof7bit's goxtool](http://prof7bit.github.io/goxtool/). This is what it looks like:

![Screenshot](https://raw.github.com/genbtc/goxgui/master/genBTCScreenshot_4.png)

Features
--------

* Stop-Loss Tab (with Stop-Loss market sells (fixed or TRAILING) & Stop-Gain market buys)
* Display asks / bids (Order Book tab)
* Display User Orders (User Orders tab)
* Place and cancel individual orders or All Orders
* Ticker in Title bar (and new Ticker Tab with auto-refresh)
* Display MtGox account balance (for fiat and crypto)
* Display MtGox lag in seconds
* Multi currency support including all gox supported fiat currencies and potential support for LTC/NMC

Stop-Loss Instructions
------------------------

"Stop-Gain Market buys" are something else entirely. if the price is going up and you dont want to be left behind, this is when you use the "negative size" to tell the bot to BUY instead of sell, once the target price is reached.

To recap:
+Size , +Price = Stop Loss Market Sell ("size" BTC will be sold at market, when price falls at or below "Price")

+Size,  -Price = TRAILING Stop Loss Market sell (same as the first one, except the stop loss target price will start off at the current price minus "Price", as the market goes up, the stop target will compensate, and should the price fall below the new adjusted target (the sell will fire and PROFITS will be taken).

-Size,  +Price = Stop GAIN market BUY ("size" BTC (the negative signifies a buy), will be BOUGHT at market, when the price climbs at or above "Price")

WARNING: -Size, -Price <---- DONT try do it, i did not create something to handle this, and it has to be coded before it can work, (refer to https://bitcointalk.org/index.php?topic=176489.msg2022346#msg2022346 ) for a theoretical run through of what it would do.


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
----------------------------
Open up the Options menu and click Preferences.

Once you enter the API key and Secret, they are encrypted in the .ini file. Previously the password they were encrypted with was hardcoded, not user-choosable and I found this odd (security hole). So I cobbled together the method that you see in my forked version, and heres the instructions.

1) Download the fork from https://github.com/genbtc/goxgui

2) The program will generate a new blank config file on first run. (Don't try to import the old one)

3) Click the Options Menu, go to Preferences, and enter your API Key and Secret

4) Enter a Password of your own choosing.......

5) Hit Apply to check for errors, and then click OK if verified.

6) The program will encrypt the API Key/Secret and store it in the INI file.

This will store your password, and auto-login everytime you launch it next time.


Issues
--------
Stop Loss:
When you go into preferences, and it says "Preferences changed, restarting market. Market restarted successfully." <- this causes Stop Loss orders to be erased (but they are still visible in the page.) An upcoming change should solve this. Until then, please do not change preferences once you have stop loss orders set up.
- Also, do not try to use negative Size and negative price, as mentioned above

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