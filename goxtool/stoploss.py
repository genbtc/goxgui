"""
a simple stop loss bot.
adjust STOP_PRICE and STOP_VOLUME to your needs.
The file can be reloaded after editing without
restarting goxtool by simply pressing the l key.
"""
import strategy
from utilities import gox2float

SIMULATION = False

class Strategy(strategy.Strategy):
    """a simple stoploss bot"""
    def __init__(self, gox):
        strategy.Strategy.__init__(self, gox)
        gox.stopOrders = []
        gox.stopbot_active = False
        gox.stopbot_executed = strategy.goxapi.Signal()

    def slot_trade(self, gox, (date, last_price, volume, typ, own)):
        """a trade message has been received"""
        if gox.stopbot_active:
            for order in gox.stopOrders:
                STOP_VOLUME = gox2float(order[1],gox.curr_base)
                STOP_PRICE = gox2float(order[2],gox.curr_quote)
                if STOP_VOLUME > 0:
                    if last_price <= STOP_PRICE:
                        self.debug("StopLoss Executed. Market Sell %s %s (last trade was at or below: $%s)" % 
                                   (order[1],gox.curr_base,order[2]))
                        gox.stopbot_executed(order,None)
                        if not SIMULATION:
                            gox.sell(0, int(STOP_VOLUME))
                elif STOP_VOLUME < 0:
                    if last_price >= STOP_PRICE:
                        self.debug("StopGain Executed. Market Buy %s %s (last trade was at or above: $%s)" % 
                                   (order[1]*-1,gox.curr_base,order[2]))
                        gox.stopbot_executed(order,None)
                        if not SIMULATION:
                            gox.buy(0, int(STOP_VOLUME)*-1)
                    