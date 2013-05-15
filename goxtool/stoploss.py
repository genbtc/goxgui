"""
a simple stop loss bot.
adjust STOP_PRICE and STOP_VOLUME to your needs.
The file can be reloaded after editing without
restarting goxtool by simply pressing the l key.
"""
import strategy
from goxapi import float2int

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
                stop_volume = float2int(order[1],gox.curr_base)
                stop_price = float2int(order[2],gox.curr_quote)
                if stop_volume > 0:
                    if stop_price < 0:
                        price_trail = last_price + stop_price
                        if len(order) == 3:                 #on the first time run...
                            order.append(stop_price)        #store the trail distance
                            order.append(price_trail)       #store the last trailing stop price
                            stop_price = price_trail        #set the stop price for this run
                        elif len(order) == 5:               #on all other subsequent runs
                            if price_trail > order[4]:      #if last trail price > old trail price 
                                order[4] = price_trail      #store a new trail price
                            stop_price = order[4]           #then set it for the current run

                    if last_price <= stop_price:
                        self.debug("StopLoss Executed. Market Sell %s %s (last trade was at or below: $%s)" % 
                                   (order[1],gox.curr_base,order[2]))
                        gox.stopbot_executed(order,None)
                        if not SIMULATION:
                            gox.sell(0, stop_volume)
                elif stop_volume < 0:
                    if last_price >= stop_price:
                        self.debug("StopGain Executed. Market Buy %s %s (last trade was at or above: $%s)" % 
                                   (abs(order[1]),gox.curr_base,order[2]))
                        gox.stopbot_executed(order,None)
                        if not SIMULATION:
                            gox.buy(0, abs(stop_volume))
                    