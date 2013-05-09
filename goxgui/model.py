from PyQt4.QtCore import QAbstractTableModel
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QVariant
from PyQt4.QtCore import SIGNAL
import utilities
import abc
import operator

class Model(QAbstractTableModel):
    '''
    Model representing a collection of orders.
    '''

    # orders smaller than this value will be grouped
    GROUP_ORDERS = 0.6

    def __init__(self, parent, market, headerdata):
        QAbstractTableModel.__init__(self, parent)
        self.__market = market
        self.__market.signal_orderbook_changed.connect(self.slot_changed)
        self.__headerdata = headerdata
        self.__data = []

    # start slots

    def slot_changed(self, orderbook):
        self.__data = self.__parse_data(orderbook)
        self.emit(SIGNAL("layoutChanged()"))

    # end slots

    def __parse_data(self, book):
        '''
        Parses the incoming data from gox,
        converts money values to our internal money format.
        '''
        data_in = self._get_data_from_book(book)
        data_out = []

        total = 0
        count = 1
        vwap = 0
        vsize = 0
        for x in data_in:

            price = x.price
            size = x.volume

            vsize += size
            vwap += price * size

            total += size
            if vsize > utilities.float2internal(self.GROUP_ORDERS):
                vwap = utilities.gox2internal(vwap / vsize, 'USD')
                vsize = utilities.gox2internal(vsize, 'BTC')
                total = utilities.gox2internal(total, 'BTC')
                data_out.append([vwap, vsize, total])
                count = 1
                vwap = 0
                vsize = 0
            else:
                count += 1

        return data_out

    @abc.abstractmethod
    def _get_data_from_book(self, book):
        '''
        This method retrieves the orders relevant to this
        specific model from the order book.
        '''
        return []

    def get_price(self, index):
        return self.__data[index][0]

    def get_size(self, index):
        return self.__data[index][1]

    def get_total(self, index):
        return self.__data[index][2]

    # START Qt methods

    def rowCount(self, parent):
        return len(self.__data)

    def columnCount(self, parent):
        return len(self.__headerdata)

    def data(self, index, role):

        if role == Qt.TextAlignmentRole:
            return Qt.AlignRight | Qt.AlignVCenter

        if (not index.isValid()) or (role != Qt.DisplayRole):
            return QVariant()

        row = index.row()
        col = index.column()

        if col == 0:
            return QVariant(utilities.internal2str(self.get_price(row), 5))
        if col == 1:
            return QVariant(utilities.internal2str(self.get_size(row)))
        if col == 2:
            return QVariant(utilities.internal2str(self.get_total(row)))

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.__headerdata[col])
        return QVariant()

    # END Qt methods


class ModelAsk(Model):

    def __init__(self, parent, market):
        Model.__init__(self, parent, market, ['Ask $', 'Size ' + utilities.BITCOIN_SYMBOL,
            'Total ' + utilities.BITCOIN_SYMBOL])

    def _get_data_from_book(self, book):
        return book.asks


class ModelBid(Model):

    def __init__(self, parent, market):
        Model.__init__(self, parent, market, ['Bid $', 'Size ' + utilities.BITCOIN_SYMBOL,
            'Total ' + utilities.BITCOIN_SYMBOL])

    def _get_data_from_book(self, book):
        return book.bids

class ModelUserOwn(QAbstractTableModel):
    '''
    Model representing a collection of orders.
    '''

    def __init__(self, parent, market, headerdata):
        QAbstractTableModel.__init__(self, parent)
        self.__market = market
        self.__market.signal_owns_changed.connect(self.__slot_changed)
        self.__headerdata = headerdata
        self.__data = [["---",1E14,1E11,"NOT","AUTHENTICATED. NO USER ORDER DATA."]]
        
        self.lastsortascdesc = Qt.DescendingOrder
        self.lastsortcol = 1

    def __slot_changed(self, book):
        self.__data = self.__parse_data(book)
        self.emit(SIGNAL("layoutChanged()"))
        self.sort(self.lastsortcol,self.lastsortascdesc)

    def __parse_data(self, book):
        '''Parse the own user order book'''
        data_in = self._get_data_from_book(book)
        data_out = []

        for x in data_in:

            price = utilities.gox2internal(x.price,'USD')
            size = utilities.gox2internal(x.volume,'BTC')
            typ = x.typ
            oid = x.oid
            status = x.status 
            
            data_out.append([typ,price,size,status,oid])

        return data_out

    @abc.abstractmethod
    def _get_data_from_book(self, book):
        '''
        This method retrieves the orders relevant to this
        specific model from the order book.
        '''
        return []

    def get_typ(self, index):
        return self.__data[index][0]

    def get_price(self, index):
        return self.__data[index][1]

    def get_size(self, index):
        return self.__data[index][2]

    def get_status(self, index):    
        return self.__data[index][3]
    
    def get_oid(self, index):
        return self.__data[index][4]


    def rowCount(self, parent):
        return len(self.__data)

    def columnCount(self, parent):
        return len(self.__headerdata)

    def data(self, index, role):
  
        if role == Qt.TextAlignmentRole:
            return Qt.AlignRight | Qt.AlignVCenter
  
        if (not index.isValid()) or (role != Qt.DisplayRole):
            return QVariant()
  
        row = index.row()
        col = index.column()
  
        if col == 0:
            return QVariant(self.get_typ(row))
        if col == 1:
            return QVariant(utilities.internal2str(self.get_price(row), 5))
        if col == 2:
            return QVariant(utilities.internal2str(self.get_size(row)))
        if col == 3:
            return QVariant(self.get_status(row))
        if col == 4:
            return QVariant(self.get_oid(row))                

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.__headerdata[col])
        return QVariant()
    
    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.__data = sorted(self.__data, key=operator.itemgetter(Ncol))        
        if order == Qt.DescendingOrder:
            self.__data.reverse()
        self.emit(SIGNAL("layoutChanged()"))
        self.lastsortcol = Ncol
        self.lastsortascdesc = order

        
class ModelOwns(ModelUserOwn):

    def __init__(self, parent, market):
        ModelUserOwn.__init__(self, parent, market, ['Type','Price','Size','Status','Order ID'])

    def _get_data_from_book(self, book):
        return book.owns

class ModelStopOrders(QAbstractTableModel):
    '''
    Model representing a collection of stop orders.
    '''

    def __init__(self, parent, market, headerdata):
        QAbstractTableModel.__init__(self, parent)
        self.__market = market
        self.stopOrders = self.__market.gox.stopOrders = []
        self.__market.gox.stopbot_executed.connect(self.__on_signal_executed)
        self.__headerdata = headerdata
        self.__data = [["NO","  STOP ORDERS  ","YET"]]
        
        self.lastsortascdesc = Qt.DescendingOrder
        self.lastsortcol = 0

    
    def changed(self):
        self.__slot_changed()

    def __on_signal_executed(self, order, dummy_data2):
        self.stopOrders.remove(order)
        self.__slot_changed()

    def __slot_changed(self):
        self.__data = self.__parse_data()
        self.emit(SIGNAL("layoutChanged()"))
        self.sort(self.lastsortcol,self.lastsortascdesc)

    def __parse_data(self):
        '''Parse the own user order book'''
        data_in = self.stopOrders
        data_out = []
        count = 1
        for x in data_in:
            
            oid = count
            size = x[1]
            price = x[2]
  
            data_out.append([oid,size,price])
            count += 1
        return data_out
    
    def get(self,row,col):
        return self.__data[row][col]
    
    def rowCount(self, parent):
        return len(self.__data)

    def columnCount(self, parent):
        return len(self.__headerdata)
        
    def data(self, index, role):
  
        if role == Qt.TextAlignmentRole:
            return Qt.AlignRight | Qt.AlignVCenter
  
        if (not index.isValid()) or (role != Qt.DisplayRole):
            return QVariant()
  
        row = index.row()
        col = index.column()
    
        return QVariant(self.__data[row][col])
        
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.__headerdata[col])
        return QVariant()
    
    def sort(self, Ncol, order):
        """Sort table by given column number.  """
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.__data = sorted(self.__data, key=operator.itemgetter(Ncol))        
        if order == Qt.DescendingOrder:
            self.__data.reverse()
        self.emit(SIGNAL("layoutChanged()"))
        self.lastsortcol = Ncol
        self.lastsortascdesc = order
        
class ModelStops(ModelStopOrders):

    def __init__(self, parent, market):
        ModelStopOrders.__init__(self, parent, market, ['ID #','Size '+utilities.BITCOIN_SYMBOL,'Price $'])
