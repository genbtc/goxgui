from PyQt4.QtCore import QAbstractTableModel
import operator
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QVariant
from PyQt4.QtCore import SIGNAL
from utilities import *
import abc


class Model(QAbstractTableModel):
    '''
    Model representing a collection of orders.
    '''

    def __init__(self, gox, headerdata):
        QAbstractTableModel.__init__(self)
        self.gox = gox
        self.gox.orderbook.signal_changed.connect(self.__slot_changed)
        self.__headerdata = self.headerdata = headerdata
        self.__data = []

    def __slot_changed(self, book, dummy_data):
        self.__data = self.__parse_data(book)
        self.emit(SIGNAL("layoutChanged()"))

    def __parse_data(self, book):
        '''
        Parses the incoming data from gox,
        converts money values to our internal
        money format
        '''
        data_in = self._get_data_from_book(book)
        data_out = []

        total = 0
        count = 1; vwap = 0; vsize = 0
        for x in data_in:

            price = x.price
            size = x.volume
            
            vsize += size
            vwap += price * size

            total += size
            if vsize > float2internal(0.6):         #ignore anything BELOW this volume and cumulate it into the next.
                vwap = gox2internal(vwap/vsize, 'USD')
                vsize = gox2internal(vsize,'BTC')
                total = gox2internal(total,'BTC')
                data_out.append([vwap, vsize, total])
                count = 1; vwap = 0; vsize = 0
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

    # def get_sum_total(self, index):
        # return self.__data[index][3]

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
            return QVariant(internal2str(self.get_price(row), 5))
        if col == 1:
            return QVariant(internal2str(self.get_size(row)))
        if col == 2:
            return QVariant(internal2str(self.get_total(row), 5))
        # if col == 3:
            # return QVariant(internal2str(self.get_sum_total(row), 5))

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.__headerdata[col])
        return QVariant()

    # END Qt methods

BTCS = BitcoinSymbol = unichr(3647)
 
class ModelAsk(Model):

    def __init__(self, gox):
        Model.__init__(self, gox, ['Ask $', 'Size '+BTCS, 'Total '+BTCS])

    def _get_data_from_book(self, book):
        return book.asks


class ModelBid(Model):

    def __init__(self, gox):
        Model.__init__(self, gox, ['Bid $', 'Size '+BTCS, 'Total '+BTCS])

    def _get_data_from_book(self, book):
        return book.bids

class ModelUserOwn(QAbstractTableModel):
    '''
    Model representing a collection of orders.
    '''

    def __init__(self, gox, headerdata):
        QAbstractTableModel.__init__(self)
        self.gox = gox
        self.gox.orderbook.ownorders_changed.connect(self.__slot_changed)
        self.__headerdata = self.headerdata = headerdata
        self.__data = [["xxxx",1E14,1E12,"xxxxxxxx","xxxxxxxxxxNO USER ORDER DATAxxxxxxxxxxx"]]
        
        self.lastsortascdesc = Qt.DescendingOrder
        self.lastsortcol = 1

    def __slot_changed(self, book, dummy_data):
        self.__data = self.__parse_data(book)
        self.emit(SIGNAL("layoutChanged()"))
        self.sort(self.lastsortcol,self.lastsortascdesc)

    def __parse_data(self, book):
        '''Parse the own user order book'''
        data_in = self._get_data_from_book(book)
        data_out = []

        for x in data_in:

            price = gox2internal(x.price,'USD')
            size = gox2internal(x.volume,'BTC')
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

    
#     def data(self, index, role): 
#         if not index.isValid(): 
#             return QVariant() 
#         elif role != Qt.DisplayRole: 
#             return QVariant() 
#         return QVariant(self.__data[index.row()][index.column()]) 
    
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
            return QVariant(internal2str(self.get_price(row), 5))
        if col == 2:
            return QVariant(internal2str(self.get_size(row)))
        if col == 3:
            return QVariant(self.get_status(row))
        if col == 4:
            return QVariant(self.get_oid(row))                
#          
        # if col == 3:
            # return QVariant(internal2str(self.get_sum_total(row), 5))

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
    # END Qt methods
        
class ModelOwns(ModelUserOwn):

    def __init__(self, gox):
        ModelUserOwn.__init__(self, gox, ['Type','Price','Size','Status','Order ID'])

    def _get_data_from_book(self, book):
        return book.owns

class ModelStopOrders(QAbstractTableModel):
    '''
    Model representing a collection of stop orders.
    '''

    def __init__(self, gox, headerdata):
        QAbstractTableModel.__init__(self)
        gox.stopOrders = []
        gox.stopbot_executed.connect(self.__on_signal_executed)
        self.gox = gox
        self.stopOrders = self.gox.stopOrders 
        self.__headerdata = self.headerdata = headerdata
        self.__data = [["NO"," STOP ORDERS ","YET"]]
        
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
    # END Qt methods
        
class ModelStops(ModelStopOrders):

    def __init__(self, gox):
        ModelStopOrders.__init__(self, gox, ['ID #','Size '+BTCS,'Price $'])
