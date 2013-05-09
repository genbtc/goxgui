import utilities

from ConfigParser import RawConfigParser
from os import path
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QDialogButtonBox
from ui.preferences_ import Ui_Preferences
from PyQt4 import QtGui


class Preferences(QDialog):
    '''
    Represents the application preferences.
    '''
    GROUP_ORDERS = 0.6
    DEFAULT_PASSWORD = 'fffuuuuuu'
    FILENAME = 'goxgui.ini'

    def __init__(self):
        QDialog.__init__(self)

        # set up ui
        self.__ui = Ui_Preferences()
        self.__ui.setupUi(self)

        # improve ui on mac
        if utilities.platform_is_mac():
            self.__adjust_for_mac()

        # connect ui signals to logic
        self.__ui.lineEditPassword.textChanged.connect(
            self.__slot_password_changed)
        self.__ui.lineEditKey.textChanged.connect(
            self.__slot_validate_key)
        self.__ui.lineEditSecret.textChanged.connect(
            self.__slot_validate_secret)
        self.__ui.buttonBox.button(QDialogButtonBox.Apply).released.connect(
            self.__slot_validate_credentials)
        
        self.do_configfile()

    def do_configfile(self):
        # initialize config parser
        self.configparser = RawConfigParser()

        # __load or (if non-existent) create config file
        if path.isfile(self.FILENAME):
            self.__load()
        else:
            self.__init_with_defaults()
            self.__save()
            
        self.GROUP_ORDERS = float(self.configparser.get("goxgui","group_orders"))

    # start slots
    def __slot_password_changed(self):
        self.__disable_ok('Password Changed...')
        return
   
    def __slot_validate_key(self,key):

        try:
            utilities.assert_valid_key(str(key))
            self.__set_status('Key is valid.')
        except Exception as e:
            self.__disable_ok('Invalid key. %s' % e)
            return 1

    def __slot_validate_secret(self,secret):

        try:
            utilities.assert_valid_secret(str(secret))
            self.__set_status('Secret is valid.')
        except Exception as e:
            self.__disable_ok('Invalid secret. %s' % e)
            return 1

    def __slot_validate_credentials(self):

        key = str(self.__ui.lineEditKey.text())
        secret = str(self.__ui.lineEditSecret.text())

        # empty credentials are allowed
        if key == '' and secret == '':
            self.__enable_ok()
            self.__set_status("Credentials are Empty. Allowed.")
            return

        if not self.__slot_validate_key(key) and not self.__slot_validate_secret(secret):            
            self.__enable_ok()
            self.__set_status("Credentials are Valid. Click OK to Save and reload.")

    # end slots

    # start private methods

    def __init_with_defaults(self):
        self.configparser.add_section('goxgui')
        self.set('key', '')
        self.set('secret', '')
        self.set('password', self.DEFAULT_PASSWORD)
        self.set('group_orders', self.GROUP_ORDERS)

    def __load_to_gui(self):
        self.do_configfile()
        self.__ui.lineEditKey.setText(self.get('key'))
        self.__ui.lineEditSecret.setText(self.decrypt_secret())
        self.__ui.lineEditPassword.setText(self.get('password'))
        self.__set_status('')
        #populate the Various Settings, Currency tab
        self.__ui.comboBoxCurrencyFiat.clear()
        self.__ui.comboBoxCurrencyFiat.addItem(self.configparser.get("gox","quote_currency"))
        self.__ui.comboBoxCurrencyTarget.clear()
        self.__ui.comboBoxCurrencyTarget.addItem(self.configparser.get("gox","base_currency"))
        #set default order grouping 
        self.__ui.doubleSpinBoxGROUPORDERS.setValue(self.GROUP_ORDERS)
        self.GROUP_ORDERS = self.__ui.doubleSpinBoxGROUPORDERS.value()
        

    def __save_from_gui(self):
        #save settings to the configparser
        self.set('key',str(self.__ui.lineEditKey.text()))
        password = str(self.__ui.lineEditPassword.text())
        if not password:
            password = self.DEFAULT_PASSWORD 
        self.__set_encrypted_secret(
            str(self.__ui.lineEditSecret.text()),password)
        self.set('password',password)
        #save currency settings 
        self.configparser.set("gox","quote_currency",str(self.__ui.comboBoxCurrencyFiat.currentText()))
        self.configparser.set("gox","base_currency",str(self.__ui.comboBoxCurrencyTarget.currentText()))
        #save order grouping settings 
        self.configparser.set("goxgui","group_orders",str(self.__ui.doubleSpinBoxGROUPORDERS.value()))
        self.GROUP_ORDERS = self.__ui.doubleSpinBoxGROUPORDERS.value()

    def __disable_ok(self, text):
        self.__ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.__set_status(text)

    def __enable_ok(self):
        self.__ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        self.__set_status('')

    def __save(self):
        '''
        Saves the config to the .ini file
        '''
        with open(self.FILENAME, 'wb') as configfile:
            self.configparser.write(configfile)

    def __load(self):
        '''
        Loads or reloads the config from the .ini file
        '''
        self.configparser.read(self.FILENAME)

    def __set_key(self, key):
        '''
        Writes the specified key to the configuration file.
        '''
        self.set('key', key)

    def __set_encrypted_secret(self, secret, password):
        '''
        Writes the specified secret to the configuration file (encrypted).
        '''
        if secret != '':
            secret = utilities.encrypt(secret, password)
            
        self.set('secret', secret)
       
    def __set_status(self, text):
        self.__ui.labelStatus.setText(text)

    def __adjust_for_mac(self):
        '''
        Fixes some stuff that looks good on windows but bad on mac.
        '''
        # the default fixed fontA is unreadable on mac, so replace it
        fontA = QtGui.QFont('Monaco', 11)
        self.__ui.lineEditPassword.setFont(fontA)
        self.__ui.lineEditKey.setFont(fontA)
        self.__ui.lineEditSecret.setFont(fontA)

        # the default label font is too big on mac
        fontB = QtGui.QFont('Lucida Grande', 11)
        self.__ui.labelPassword.setFont(fontB)
        self.__ui.labelKeySecret.setFont(fontB)
        self.__ui.labelCurrency.setFont(fontB)

    # end private methods

    # start public methods

    def get(self, key):
        '''
        Retrieves a property from the global section
        '''
        return self.configparser.get('goxgui', key)

    def set(self, key, value):
        '''
        Stores a property to the global section
        '''
        self.configparser.set('goxgui', key, value)

    def decrypt_secret(self,password=''):
        
        secret = self.get('secret')
        if secret == '':
            return ''
        if password == '':
            password = self.get('password')

        return utilities.decrypt(secret, password)

    def show(self):
        '''
        Shows the preference dialog.
        @return: True if the user accepted, false otherwise
        '''
        self.__load_to_gui()
        result = self.exec_()
        return result == QDialog.Accepted

    def apply(self):
        '''
        Applies the user changes.
        Changes made by the user during show()
        do not propagate until apply() is called.
        '''
        self.__save_from_gui()
        self.__save()

    # end public methods
