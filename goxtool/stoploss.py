"""
a simple stop loss bot.
adjust STOP_PRICE and STOP_VOLUME to your needs.
The file can be reloaded after editing without
restarting goxtool by simply pressing the l key.
"""
import strategy

BTC = 1e8
USD = 1e5

SIMULATION = False

class Strategy(strategy.Strategy):
    """a simple stoploss bot"""
    def __init__(self, gox):
        strategy.Strategy.__init__(self, gox)
        gox.stopbot_active = False
        gox.stopbot_executed = strategy.goxapi.Signal()

    def slot_trade(self, gox, (date, last_price, volume, typ, own)):
        """a trade message has been received"""
        if gox.stopbot_active:
            for order in gox.stopOrders:
                STOP_VOLUME = order[1] * BTC
                STOP_PRICE = order[2] * USD
                if last_price <= STOP_PRICE:
                    self.debug("StopLoss Executed. Market Sell %s BTC (last trade was at or below: $%s)" % (order[1],order[2]))
                    gox.stopbot_executed(order,None)
                    if not SIMULATION:
                        gox.sell(0, int(STOP_VOLUME))