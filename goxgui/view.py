from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QTextCursor
from PyQt4.QtGui import QApplication
from adaptor import Adaptor
from ui.main_window_ import Ui_MainWindow
from model import ModelAsk,ModelBid,ModelOwns,ModelStops
import utilities
import time
import os


class View(QMainWindow):
    '''
    Represents the combined view / control.
    '''


    def __init__(self, gox, secret, logfile):

        self.logfile = logfile

        QMainWindow.__init__(self)

        # setup UI
        self.mainWindow = Ui_MainWindow()
        self.mainWindow.setupUi(self)

        # setup gox objects
        self.gox = gox
        self.secret = secret
        
        self.passphrase = ''

        # associate log channels with their check boxes
        self.logchannels = [
            [self.mainWindow.tickerCheckBox, 'tick'],
            [self.mainWindow.tradesCheckBox, 'TRADE'],
            [self.mainWindow.depthCheckBox, 'depth'],
        ]
        
        # connect to gox signals
        self.adaptor = Adaptor(self.gox)
        self.adaptor.signal_log.connect(self.log)
        self.adaptor.signal_wallet.connect(self.display_wallet)
        self.adaptor.signal_orderlag.connect(self.display_orderlag)
        self.adaptor.signal_userorder.connect(self.display_userorder)
        self.adaptor.signal_ticker.connect(self.slot_ticker)

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
        #Password TAB
        self.mainWindow.passwordButton.released.connect(self.load_credentials)
        
        #OrderBook TAB
        self.mainWindow.tableAsk.clicked.connect(self.update_edit_from_ask_book)
        self.mainWindow.tableBid.clicked.connect(self.update_edit_from_bid_book)
        
        #User Orders TAB
        self.modelOwns = ModelOwns(self.gox)
        self.mainWindow.tableUserOrders.setModel(self.modelOwns)
        self.mainWindow.tableUserOrders.resizeColumnsToContents()
        self.mainWindow.tableUserOrders.clicked.connect(self.userorder_selected)
        
        #Trading Box
        self.mainWindow.pushButtonGo.released.connect(self.execute_trade)
        self.mainWindow.pushButtonCancel.released.connect(self.cancel_order)
        self.mainWindow.pushButtonSize.released.connect(self.recalculate_size)
        self.mainWindow.pushButtonPrice.released.connect(self.update_edit_on_button)
        self.mainWindow.pushButtonTotal.released.connect(self.recalculate_total)
        
        self.mainWindow.textBrowserStatus.anchorClicked.connect(self.order_selected)
        
        #reset the mtgox socketIO socket
        self.mainWindow.pushbuttonResetSocket.released.connect(self.restart_gox)
        
        #create the stop orders window.
        self.modelStops = ModelStops(self.gox)
        self.mainWindow.tableStopOrders.setModel(self.modelStops)
        self.mainWindow.tableStopOrders.resizeColumnsToContents()

        #add stop orders into the stop database
        self.mainWindow.pushButton1StopAdd.released.connect(self.add_stopOrder)
        #on click, put Stop Order ID into the cancel button box.
        self.mainWindow.tableStopOrders.clicked.connect(self.stopOrder_selected)
        #remove a stop order
        self.mainWindow.pushButtonStopRemove.released.connect(self.remove_stopOrder)
        #activate the bot with the checkbox.
        self.mainWindow.checkBoxActivateStopLossBot.clicked.connect(self.stopbot_act_deact)
        
        
        self.show()
        self.raise_()


    def add_stopOrder(self):
        size = float(self.mainWindow.lineEdit1StopSize.text())
        price = float(self.mainWindow.lineEdit2StopPrice.text())
        self.mainWindow.lineEdit1StopSize.setText('')
        self.mainWindow.lineEdit2StopPrice.setText('')
        oid = len(self.gox.stopOrders)+1
        self.gox.stopOrders.append([oid,size,price])
        self.modelStops.changed()

    def stopOrder_selected(self, index):
        self.mainWindow.lineEdit3StopID.setText(str(self.modelStops.get(index.row(),0)))        
        
    def remove_stopOrder(self):
        oid = self.mainWindow.lineEdit3StopID.text()
        oid = int(oid)-1
        self.mainWindow.lineEdit3StopID.setText('')
        self.gox.stopOrders.remove(self.gox.stopOrders[oid])
        self.modelStops.changed()

    def stopbot_act_deact(self):
        if self.mainWindow.checkBoxActivateStopLossBot.isChecked():
            self.gox.stopbot_active = True
        else:
            self.gox.stopbot_active = False

    def slot_ticker(self,bid,ask):
        #change the title to match any updates from the ticker channel
        newtitle = "MtGox Trading UI - Bid: {0}, Ask: {1}".format(bid/1E5,ask/1E5)
        self.setWindowTitle(QApplication.translate("MainWindow", newtitle, None, QApplication.UnicodeUTF8))
        
    def restart_gox(self):
        self.gox.client.debug("Restarting MtGox SocketIO Client")
        self.gox.client.socket.close()
        self.gox.client.connected = False

    def get_selected_trade_type(self):
        return 'BUY' if self.mainWindow.radioButtonBuy.isChecked() else 'SELL'

    def set_selected_trade_type(self, trade_type):
        if trade_type == 'BUY':
            self.mainWindow.radioButtonBuy.toggle()
        else:
            self.mainWindow.radioButtonSell.toggle()

    def log(self, text):
        text = self.prepend_date(text)
        self.log_to_file(text)
        
        doOutput = False
        
        for entry in self.logchannels:
            if not entry[0].isChecked():
                if entry[1] in text:
                    return

        if self.mainWindow.systemCheckBox.isChecked():
            doOutput = True
        else:
            for entry in self.logchannels:
                if entry[1] in text:
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
        
    def userorder_selected(self, index):
        self.set_order_id(self.modelOwns.get_oid(index.row()))

    def save_credentials(self):
        '''
        Tries to encrypt the credentials entered by the user
        and save them to the configuration file.
        Incomplete or inplausible credentials will not be saved.
        '''
        def error_message(reason):
            phrase = 'Credentials not saved'
            self.status_message(phrase + reason)
            return 0

        key = str(format(self.mainWindow.lineEditKey.text()))
        secret = str(self.mainWindow.lineEditSecret.text())
           
        if key == '':
            return error_message(" (empty key).")
        if secret == '':
            return error_message(" (empty secret).")


        self.passphrase = str(self.mainWindow.passwordLineEdit.text())
        if self.passphrase == '':
            self.mainWindow.tabWidget_1.setCurrentIndex(2)
            return error_message(" (invalid password).")
                
        try:
            utilities.assert_valid_key(key)
        except Exception:
            return error_message(" (invalid key).")
        
        try:
            secret = utilities.encrypt(secret, self.passphrase)
        except Exception:
            return error_message(" (invalid secret).")

        self.gox.config.set("gox", "secret_key", key)
        self.gox.config.set("gox", "secret_secret", secret)
        self.gox.config.save()
        self.load_credentials()

    def load_credentials(self):
        '''
        Tries to load the credentials from the configuration file
        and display them to the user. If the credentials in the
        configuration file are invalid, they will not be loaded.
        '''

        key = self.gox.config.get_string("gox", "secret_key")
        secret = self.gox.config.get_string("gox", "secret_secret")

        self.passphrase = str(self.mainWindow.passwordLineEdit.text())
        try:
            utilities.assert_valid_key(key)
            secret = utilities.decrypt(secret, self.passphrase)
        except Exception:
            key = ''
            secret = ''

        self.secret.key = key
        self.secret.secret = secret
        if not key == '' and not secret == '':
            self.mainWindow.lineEditKey.setPlaceholderText('Loaded Key From File')
            self.mainWindow.lineEditSecret.setPlaceholderText('Decrypted Secret Using Password')
        self.mainWindow.tabWidget_1.setCurrentIndex(0)
        self.status_message("Credentials changed. Restarting MtGox Client")
        self.restart_gox()
        
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
            if status == 'post-pending':
                self.set_order_id(oid)

    def cancel_order(self):
        order_id = self.get_order_id()
        self.status_message(
            "Cancelling order <a href=\"{0}\">{0}</a>...".format(order_id))
        self.gox.cancel(order_id)
        
    def update_edit_from_ask_book(self, index):
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
            