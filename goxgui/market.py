from PyQt4.QtCore import QObject
from PyQt4.QtCore import pyqtSignal
import goxapi
import utilities
import time
import json

class Market(QObject):
    '''
    Wrapper for gox object used to decouple gui code
    from market implementation.
    '''

    signal_log = pyqtSignal(str)
    signal_wallet = pyqtSignal()
    signal_orderlag = pyqtSignal('long long', str)
    signal_userorder = pyqtSignal('long long', 'long long', str, str, str)
    signal_orderbook_changed = pyqtSignal(object)
    signal_owns_changed = pyqtSignal(object)
    signal_ticker = pyqtSignal('long long', 'long long')
    signal_stopbot_executed = pyqtSignal()    

    def __init__(self, preferences):
        QObject.__init__(self)
        self.__preferences = preferences
        
    def __create_gox(self):

        config = goxapi.GoxConfig("goxgui.ini")
        secret = goxapi.Secret(config)
        secret.key = self.__preferences.get('key')
        secret.secret = self.__preferences.decrypt_secret()
        gox = goxapi.Gox(secret, config)

        gox.signal_debug.connect(self.slot_log)
        gox.signal_wallet.connect(self.slot_wallet_changed)
        gox.signal_orderlag.connect(self.slot_orderlag)
        gox.signal_userorder.connect(self.slot_userorder)
        gox.orderbook.signal_changed.connect(self.slot_orderbook_changed)
        gox.orderbook.signal_owns_changed.connect(self.slot_owns_changed)        
        gox.signal_ticker.connect(self.slot_ticker)
        
        return gox

    # start slots

    def slot_log(self, dummy_gox, (text)):
        self.signal_log.emit(text)

    def slot_orderbook_changed(self, orderbook, dummy):
        self.signal_orderbook_changed.emit(orderbook)
        
    def slot_owns_changed(self, orderbook, dummy):
        self.signal_owns_changed.emit(orderbook)

    def slot_orderlag(self, dummy_sender, (ms, text)):
        self.signal_orderlag.emit(ms, text)

    def slot_wallet_changed(self, dummy_gox, (text)):
        self.signal_wallet.emit()

    def slot_userorder(self, dummy_sender, data):
        (price, size, order_type, oid, status_message) = data
        self.signal_userorder.emit(
            price, size, order_type, oid, status_message)

    def slot_ticker(self, dummy_sender, (bid, ask)):
        self.signal_ticker.emit(bid, ask)
    
    # end slots

    def start(self):
        '''
        Activates the market
        '''
        self.gox = self.__create_gox()
        self.ticker = self.initialize_ticker()
        self.gox.start()

    def stop(self):
        '''
        Deactivates the market
        '''
        self.gox.stop()
        del self.gox
        time.sleep(1)

    def buy(self, price, size):
        '''
        Places buy order
        '''
        sizeGox = utilities.internal2gox(size, 'BTC')
        priceGox = utilities.internal2gox(price, 'USD')
        self.gox.buy(priceGox, sizeGox)

    def sell(self, price, size):
        '''
        Places sell order
        '''
        sizeGox = utilities.internal2gox(size, 'BTC')
        priceGox = utilities.internal2gox(price, 'USD')
        self.gox.sell(priceGox, sizeGox)

    def cancel(self, order_id):
        '''
        Cancels order
        '''
        self.gox.cancel(order_id)

    def cancel_by_type(self, typ=None):
        '''
        Cancels order by type
        '''
        self.gox.cancel_by_type(typ)
                


    def get_balance(self, currency):
        '''
        Returns the account balance for the specified currency
        '''
        return self.gox.wallet[currency]

    def initialize_ticker(self):
        use_ssl = self.gox.config.get_bool("gox", "use_ssl")
        proto = {True: "https", False: "http"}[use_ssl]
        bcur = self.gox.curr_base
        qcur = self.gox.curr_quote
        class Ticker(object):
            def __init__(self):
                self.buy = None
                self.sell = None
                self.last = None
                self.volume = None
                self.high = None
                self.low = None
                self.avg = None
                self.vwap = None
                self.refresh_both()
            def refresh_both(self):
                self.refresh_ticker2()
                self.refresh_tickerfast()
            def refresh_tickerfast(self):
                ticker_fast = goxapi.http_request(proto + "://" +  goxapi.HTTP_HOST + "/api/2/" +  bcur + qcur + "/money/ticker_fast")
                self.ticker_fast = json.loads(ticker_fast)["data"]
                self.create_fast(self.ticker_fast)                
            def refresh_ticker2(self):
                ticker2 = goxapi.http_request(proto + "://" +  goxapi.HTTP_HOST + "/api/2/" + bcur + qcur + "/money/ticker")
                self.ticker2 = json.loads(ticker2)["data"]
                self.create_ticker2(self.ticker2)
            def create_fast(self,ticker_fast):
                self.buy = ticker_fast["buy"]["value"]
                self.sell = ticker_fast["sell"]["value"]
                self.last = ticker_fast["last"]["value"]
            def create_ticker2(self,ticker2):
                self.buy = ticker2["buy"]["value"]
                self.sell = ticker2["sell"]["value"]
                self.last = ticker2["last"]["value"]
                self.volume = ticker2["vol"]["value"]
                self.volumestr = ticker2["vol"]["display"]
                self.high = ticker2["high"]["value"]
                self.low = ticker2["low"]["value"]
                self.avg = ticker2["avg"]["value"]
                self.vwap = ticker2["vwap"]["value"]

        return Ticker()