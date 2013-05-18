from PyQt4.QtCore import QAbstractTableModel
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QVariant
from PyQt4.QtCore import SIGNAL
import utilities
import operator

class Model(QAbstractTableModel):
    '''
    Model representing a collection of orders.
    '''

    def __init__(self, parent, market, preferences, headerdata):
        QAbstractTableModel.__init__(self, parent)
        self.market = market
        self.preferences = preferences
        self.market.signal_orderbook_changed.connect(self.slot_changed)
        self.headerdata = headerdata
        self._data = []

    # start slots
    def _get_data_from_book(self, book):
        pass
    
    def slot_changed(self, orderbook):
        self._data = self.__parse_data(self._get_data_from_book(orderbook))
        self.emit(SIGNAL("layoutChanged()"))

    # end slots

    def __parse_data(self, book):
        '''
        Parses the incoming data from gox,
        converts money values to our internal money format.
        '''
        data_out = []
        count = 1
        total = 0
        vwap = 0
        vsize = 0
        group_size = utilities.float2internal(self.preferences.GROUP_ORDERS)
        for x in book:

            vsize += x.volume
            vwap += x.price * x.volume
            total += x.volume
            
            if vsize > group_size:
                vwap = vwap / vsize
                data_out.append([vwap, vsize, total])
                count = 1
                vwap = 0
                vsize = 0
            else:
                count += 1

        return data_out

    def get_price(self, index):
        return self._data[index][0]

    def get_size(self, index):
        return self._data[index][1]

    def get_total(self, index):
        return self._data[index][2]

    # START Qt methods

    def rowCount(self, parent):
        return len(self._data)

    def columnCount(self, parent):
        return len(self.headerdata)

    def data(self, index, role):

        if role == Qt.TextAlignmentRole:
            return Qt.AlignRight | Qt.AlignVCenter

        if (not index.isValid()) or (role != Qt.DisplayRole):
            return QVariant()

        row = index.row()
        col = index.column()

        if col == 0:
            return QVariant(utilities.gox2str(self.get_price(row),self.market.curr_quote,5))
        elif col == 1:
            return QVariant(utilities.gox2str(self.get_size(row),self.market.curr_base,8))
        elif col == 2:
            return QVariant(utilities.gox2str(self.get_total(row),self.market.curr_base,6))

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()

    # END Qt methods


class ModelAsk(Model):

    def __init__(self, parent, market, preferences):
        Model.__init__(self, parent, market, preferences, ['Ask $', 'Size ' + utilities.BITCOIN_SYMBOL,
            'Total ' + utilities.BITCOIN_SYMBOL])

    def _get_data_from_book(self, book):
        return book.asks

class ModelBid(Model):

    def __init__(self, parent, market, preferences):
        Model.__init__(self, parent, market, preferences, ['Bid $', 'Size ' + utilities.BITCOIN_SYMBOL,
            'Total ' + utilities.BITCOIN_SYMBOL])

    def _get_data_from_book(self, book):
        return book.bids

class ModelUserOwn(QAbstractTableModel):
    '''
    Model representing a collection of orders.
    '''

    def __init__(self, parent, market, preferences, headerdata):
        QAbstractTableModel.__init__(self, parent)
        self.market = market
        self.market.signal_owns_changed.connect(self.__slot_changed)
        self._data = [["---",1E14,1E11,"NOT","AUTHENTICATED. NO USER ORDER DATA."]]
        self.headerdata = headerdata
        self.lastsortascdesc = Qt.DescendingOrder
        self.lastsortcol = 1

    def __slot_changed(self, book):
        self._data = self.__parse_data(book)
        self.emit(SIGNAL("layoutChanged()"))
        self.sort(self.lastsortcol,self.lastsortascdesc)

    def __parse_data(self, book):
        '''Parse the own user order book'''
        data_out = []

        for x in book:
            data_out.append([x.typ,x.price,x.volume,x.status,x.oid])

        return data_out

    def get_typ(self, index):
        return self._data[index][0]
    
    def get_price(self, index):
        return self._data[index][1]

    def get_size(self, index):
        return self._data[index][2]
    
    def get_status(self, index):    
        return self._data[index][3]
    
    def get_oid(self, index):
        return self._data[index][4]


    def rowCount(self, parent):
        return len(self._data)

    def columnCount(self, parent):
        return len(self.headerdata)

    def data(self, index, role):
  
        if role == Qt.TextAlignmentRole:
            return Qt.AlignRight | Qt.AlignVCenter
  
        if (not index.isValid()) or (role != Qt.DisplayRole):
            return QVariant()
  
        row = index.row()
        col = index.column()
  
        if col == 0:
            return QVariant(self.get_typ(row))
        elif col == 1:
            return QVariant(utilities.gox2str(self.get_price(row),self.market.curr_quote,5))
        elif col == 2:
            return QVariant(utilities.gox2str(self.get_size(row),self.market.curr_base,8))
        elif col == 3:
            return QVariant(self.get_status(row))
        elif col == 4:
            return QVariant(self.get_oid(row))                

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()
    
    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self._data = sorted(self._data, key=operator.itemgetter(Ncol))        
        if order == Qt.DescendingOrder:
            self._data.reverse()
        self.emit(SIGNAL("layoutChanged()"))
        self.lastsortcol = Ncol
        self.lastsortascdesc = order

        
class ModelOwns(ModelUserOwn):

    def __init__(self, parent, market, preferences):
        ModelUserOwn.__init__(self, parent, market, preferences, ['Type','Price','Size','Status','Order ID'])

class ModelStopOrders(QAbstractTableModel):
    '''
    Model representing a collection of stop orders.
    '''

    def __init__(self, parent, market, headerdata):
        QAbstractTableModel.__init__(self, parent)
        self.market = market
        self.market.gox.stopbot_executed.connect(self.__on_signal_executed)
        self.headerdata = headerdata
        self._data = [["NO","  STOP ORDERS  ","YET"]]
        
        self.lastsortascdesc = Qt.DescendingOrder
        self.lastsortcol = 0

    
    def changed(self):
        self.__slot_changed()

    def __on_signal_executed(self, order, dummy_data2):
        self.market.gox.stopOrders.remove(order)
        self.__slot_changed()

    def __slot_changed(self):
        self._data = self.__parse_data()
        self.emit(SIGNAL("layoutChanged()"))
        self.sort(self.lastsortcol,self.lastsortascdesc)

    def __parse_data(self):
        '''Parse the own user order book'''
        data_out = []
        count = 1
        for x in self.market.gox.stopOrders:
            data_out.append([count,x[1],x[2]])
            count += 1
        return data_out
    
    def get(self,row,col):
        return self._data[row][col]
    
    def rowCount(self, parent):
        return len(self._data)

    def columnCount(self, parent):
        return len(self.headerdata)
        
    def data(self, index, role):
  
        if role == Qt.TextAlignmentRole:
            return Qt.AlignRight | Qt.AlignVCenter
  
        if (not index.isValid()) or (role != Qt.DisplayRole):
            return QVariant()
  
        row = index.row()
        col = index.column()
    
        return QVariant(self._data[row][col])
        
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()
    
    def sort(self, Ncol, order):
        """Sort table by given column number.  """
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self._data = sorted(self._data, key=operator.itemgetter(Ncol))        
        if order == Qt.DescendingOrder:
            self._data.reverse()
        self.emit(SIGNAL("layoutChanged()"))
        self.lastsortcol = Ncol
        self.lastsortascdesc = order
        
class ModelStops(ModelStopOrders):

    def __init__(self, parent, market):
        ModelStopOrders.__init__(self, parent, market, ['ID #','Size '+utilities.BITCOIN_SYMBOL,'Price $'])
