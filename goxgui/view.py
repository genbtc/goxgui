from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QTextCursor
from adaptor import Adaptor
from ui.main_window_ import Ui_MainWindow
from model import ModelAsk
from model import ModelBid
from model import ModelOwns
import utilities
import time
import os


class View(QMainWindow):
    '''
    Represents the combined view / control.
    '''

    PASSPHRASE = 'fffuuuuuuu'

    def __init__(self, gox, secret, logfile):

        self.logfile = logfile

        QMainWindow.__init__(self)

        # setup UI
        self.mainWindow = Ui_MainWindow()
        self.mainWindow.setupUi(self)

        # setup gox objects
        self.gox = gox
        self.secret = secret

        # connect to gox signals
        self.adaptor = Adaptor(self.gox)
        self.adaptor.signal_log.connect(self.log)
        self.adaptor.signal_wallet.connect(self.display_wallet)
        self.adaptor.signal_orderlag.connect(self.display_orderlag)
        self.adaptor.signal_userorder.connect(self.display_userorder)

        # initialize and connect bid / ask table models
        self.modelAsk = ModelAsk(self.gox)
        self.mainWindow.tableAsk.setModel(self.modelAsk)
        self.modelBid = ModelBid(self.gox)
        self.mainWindow.tableBid.setModel(self.modelBid)

        # connect signals from UI Qt components to our own slots
        #Account Balance TAB
        self.mainWindow.pushButtonWalletA.released.connect(self.set_trade_size_from_wallet)
        self.mainWindow.pushButtonWalletB.released.connect(self.set_trade_total_from_wallet)

        #Auth TAB
        self.mainWindow.pushButtonApply.released.connect(self.save_credentials)
        
        #OrderBook TAB
        self.mainWindow.tableAsk.clicked.connect(self.update_edit_from_ask_book)
        self.mainWindow.tableBid.clicked.connect(self.update_edit_from_bid_book)
        
        #User Orders TAB
        self.modelOwns = ModelOwns(self.gox)
        self.mainWindow.tableUserOrders.setModel(self.modelOwns)
        
        #Trading Box
        self.mainWindow.pushButtonGo.released.connect(self.execute_trade)
        self.mainWindow.pushButtonCancel.released.connect(self.cancel_order)
        self.mainWindow.pushButtonSize.released.connect(self.recalculate_size)
        self.mainWindow.pushButtonPrice.released.connect(self.update_edit_on_button)
        self.mainWindow.pushButtonTotal.released.connect(self.recalculate_total)
        
        self.mainWindow.textBrowserStatus.anchorClicked.connect(self.order_selected)
        

        # load credentials from configuration file
        self.load_credentials()

        self.show()
        self.raise_()

    def get_selected_trade_type(self):
        return 'BUY' if self.mainWindow.radioButtonBuy.isChecked() else 'SELL'

    def set_selected_trade_type(self, trade_type):
        if trade_type == 'BUY':
            self.mainWindow.radioButtonBuy.toggle()
        else:
            self.mainWindow.radioButtonSell.toggle()

    def log(self, text):
        text = self.prepend_date(text)
        doOutput = False
        
        self.log_to_file(text)
        
        channels = {"tick":self.mainWindow.tickerCheckBox,
                   "TRADE":self.mainWindow.tradesCheckBox,
                   "depth":self.mainWindow.depthCheckBox}
           
        for k,v in channels.iteritems():
            if not v.isChecked():
                if k in text:
                    return
                
        if self.mainWindow.systemCheckBox.isChecked():
            doOutput = True
        else:
            for k in channels.iterkeys():
                if k in text:
                    doOutput = True

        if doOutput:
            self.mainWindow.textBrowserLog.append(text)

    def prepend_date(self, text):
        millis = int(round(time.time() * 1000)) % 1000
        return '{}.{:0>3} {}'.format(time.strftime('%X'), millis, text)

    def log_to_file(self, text):
        self.logfile.write('{}{}'.format(text, os.linesep))

    def status_message(self, text):
        # call move cursor before append to work around link clicking bug
        # see: https://bugreports.qt-project.org/browse/QTBUG-539
        self.mainWindow.textBrowserStatus.moveCursor(QTextCursor.End)
        text = self.prepend_date(text)
        self.mainWindow.textBrowserStatus.append(text)
        self.log_to_file(text)

    def set_wallet_btc(self, value):
        self.mainWindow.pushButtonWalletA.setEnabled(value > 0)
        self.mainWindow.pushButtonWalletA.setText(
            'BTC: ' + utilities.internal2str(value))

    def set_wallet_usd(self, value):
        self.mainWindow.pushButtonWalletB.setEnabled(value > 0)
        self.mainWindow.pushButtonWalletB.setText(
            'USD: ' + utilities.internal2str(value, 5))

    def get_trade_size(self):
        value = self.mainWindow.doubleSpinBoxBtc.value()
        return utilities.float2internal(value)

    def set_trade_size(self, value):
        value_float = utilities.internal2float(value)
        self.mainWindow.doubleSpinBoxBtc.setValue(value_float)

    def get_trade_price(self):
        value = self.mainWindow.doubleSpinBoxPrice.value()
        return utilities.float2internal(value)

    def set_trade_price(self, value):
        value_float = utilities.internal2float(value)
        self.mainWindow.doubleSpinBoxPrice.setValue(value_float)

    def get_trade_total(self):
        value = self.mainWindow.doubleSpinBoxTotal.value()
        return utilities.float2internal(value)

    def set_trade_total(self, value):
        value_float = utilities.internal2float(value)
        self.mainWindow.doubleSpinBoxTotal.setValue(value_float)

    def get_order_id(self):
        return str(self.mainWindow.lineEditOrder.text())

    def set_order_id(self, text):
        self.mainWindow.lineEditOrder.setText(text)

    def order_selected(self, url):
        self.set_order_id(str(url.toString()))

    def save_credentials(self):
        '''
        Tries to encrypt the credentials entered by the user
        and save them to the configuration file.
        Incomplete or inplausible credentials will not be saved.
        '''

        key = str(format(self.mainWindow.lineEditKey.text()))
        secret = str(self.mainWindow.lineEditSecret.text())

        if key == '':
            self.status_message("Credentials not saved (empty key).")
            return

        if secret == '':
            self.status_message("Credentials not saved (empty secret).")
            return

        try:
            utilities.assert_valid_key(key)
        except Exception:
            self.status_message("Credentials not saved (invalid key).")
            return

        try:
            secret = utilities.encrypt(secret, View.PASSPHRASE)
        except Exception:
            self.status_message("Credentials not saved (invalid secret).")
            return

        self.gox.config.set("gox", "secret_key", key)
        self.gox.config.set("gox", "secret_secret", secret)
        self.gox.config.save()
        self.status_message("Credentials changed. Please restart application.")

    def load_credentials(self):
        '''
        Tries to load the credentials from the configuration file
        and display them to the user. If the credentials in the
        configuration file are invalid, they will not be loaded.
        '''

        key = self.gox.config.get_string("gox", "secret_key")
        secret = self.gox.config.get_string("gox", "secret_secret")

        try:
            utilities.assert_valid_key(key)
            secret = utilities.decrypt(secret, View.PASSPHRASE)
        except Exception:
            key = ''
            secret = ''

        self.secret.key = key
        self.mainWindow.lineEditKey.setText(key)
        self.secret.secret = secret
        self.mainWindow.lineEditSecret.setText(secret)

    def display_wallet(self):
        self.set_wallet_usd(utilities.gox2internal(self.gox.wallet['USD'], 'USD'))
        self.set_wallet_btc(utilities.gox2internal(self.gox.wallet['BTC'], 'BTC'))

    def set_trade_size_from_wallet(self):
        self.set_trade_size(utilities.gox2internal(self.gox.wallet['BTC'], 'BTC'))
        self.set_selected_trade_type('SELL')

    def set_trade_total_from_wallet(self):
        self.set_trade_total(utilities.gox2internal(self.gox.wallet['USD'], 'USD'))
        self.set_selected_trade_type('BUY')

    def display_orderlag(self, ms, text):
        self.mainWindow.labelOrderlag.setText('Trading Lag: ' + text)

    def execute_trade(self):

        trade_type = self.get_selected_trade_type()

        size = self.get_trade_size()
        price = self.get_trade_price()
        total = self.get_trade_total()

        trade_name = 'BID' if trade_type == 'BUY' else 'ASK'

        self.status_message('Placing order: {0} {1} BTC at $ {2} USD (total $ {3} USD)...'.format(# @IgnorePep8
            trade_name,
            utilities.internal2str(size),
            utilities.internal2str(price, 5),
            utilities.internal2str(total, 5)))

        sizeGox = utilities.internal2gox(size, 'BTC')
        priceGox = utilities.internal2gox(price, 'USD')

        mapdict = {"BUY":self.gox.buy,"SELL":self.gox.sell}
        mapdict[trade_type](priceGox, sizeGox)

    def recalculate_size(self):

        price = self.get_trade_price()
        if price == 0:
            return

        total = self.get_trade_total()
        size = utilities.divide_internal(total, price)
        self.set_trade_size(size)

    def recalculate_total(self):

        price = self.get_trade_price()
        size = self.get_trade_size()
        total = utilities.multiply_internal(price, size)
        self.set_trade_total(total)

    def display_userorder(self, price, size, order_type, oid, status):

        size = utilities.gox2internal(size, 'BTC')
        price = utilities.gox2internal(price, 'USD')

        size = utilities.internal2str(size)
        price = utilities.internal2str(price)

        if order_type == '':
            self.status_message("Order <a href=\"{0}\">{0}</a> {1}.".format(
                oid, status))
            if status == 'removed' and self.get_order_id() == oid:
                self.set_order_id('')
        else:
            self.status_message("{0} size: {1}, price: {2}, oid: <a href=\"{3}\">{3}</a> - {4}".format(# @IgnorePep8
                str.upper(str(order_type)), size, price, oid, status))
            self.set_order_id(oid)

    def cancel_order(self):
        order_id = self.get_order_id()
        self.status_message(
            "Cancelling order <a href=\"{0}\">{0}</a>...".format(order_id))
        self.gox.cancel(order_id)
        
    def update_edit_from_ask_book(self, index):
        #useless since I split into two functions.
        #the split was done because the signal could not transmit additional arguments  and...
        #i have no way to tell the two apart.
        
        #trade_type = self.get_selected_trade_type()
        #mapdict = {"BUY":self.modelBid,"SELL":self.modelAsk}
        self.set_trade_price(self.modelAsk.get_price(index.row()))
        self.set_trade_size(self.modelAsk.get_size(index.row()))
        self.set_selected_trade_type('SELL')
        
    def update_edit_from_bid_book(self, index):
        self.set_trade_price(self.modelBid.get_price(index.row()))
        self.set_trade_size(self.modelBid.get_size(index.row()))
        self.set_selected_trade_type('BUY')
       

    def update_edit_on_button(self):
        trade_type = self.get_selected_trade_type()
        mapdict = {"BUY":self.modelBid,"SELL":self.modelAsk}
        self.set_trade_price(mapdict[trade_type].get_price(0))
        self.set_trade_size(mapdict[trade_type].get_size(0))        
            