/*
my eurusd 1min trader
*/

// Data Types: int, double, bool, string, color, datetime

/*
List of Simple Predefined Names of Variables
Ask - last known sell-price of a current security;
Bid - last known buy-price of a current security;
Bars - number of bars on a current chart;
Point - point size of a current security in quote currency;
Digits - number of digits after a decimal point in the price of a current security.

   double bid   =MarketInfo("GBPUSD",MODE_BID); // Request for the value of Bid
   double ask   =MarketInfo("GBPUSD",MODE_ASK); // Request for the value of Ask
   double point =MarketInfo("GBPUSD",MODE_POINT);//Request for Point

List of Predefined Names of Arrays-Timeseries
Time - opening time of each bar on the current chart;
Open - opening price of each bar on the current chart;
Close - closing price of each bar on the current chart;
High - maximal price of each bar on the current chart;
Low - minimal price of each bar on the current chart;
Volume - tick volume of each bar on the current chart.
*/

// set params
extern double TAKE_PROFIT = 110.0;
extern double STOP_LOSS = 355.0;
extern double ENTRY = 23.0;
extern double WAIT_FOR = 32.0;
extern double EXIT_AT = 390.0;
extern double LOT_SIZE = 0.01;
string VERSION = "v0.1.0";

string symbol;
int BarsPrev;

int init()
{
   Alert("init...");
   symbol = Symbol();
   BarsPrev = Bars;
   return(0);
}


int deinit()
{
   Alert("deinit...");
   return(0);
}


int start() {
   if (Bars != BarsPrev) {
      Alert("Bars = ", Bars);
      BarsPrev = Bars;
      int ticket = CreateTrade();
   }
   return(0);
}

/*
Market order - is an executed order to buy or sell assets for a symbol (security). A market order is displayed in the symbol window until the order is closed.
Pending order is a trade order to buy or sell assets for a security (a symbol) when the preset price level is reached. Pending order is displayed in the symbol window until it becomes a market order or is deleted.
Trade Request is a command made by a program or by a trader in order to perform a trade.
Trade is opening, closing or modification of market and pending orders.

    OrderSend() - to open market and pending orders;
    OrderClose() and OrderCloseBy() - to close market orders;
    OrderDelete() - to delete pending orders;
    OrderModify() - to modify market and pending orders.

Buy is a market order that defines buying of assets for a symbol.
Sell is a market order that defines selling of assets for a symbol.
BuyLimit is a pending order to buy assets for a security at a price lower than the current one. The order will be executed (modified into market order Buy) if the Ask price reaches or falls below the price set in the pending order.
SellLimit is a pending order to sell assets for a security at a price higher than the current one. The order will be executed (modified into market order Sell) if the Bid price reaches or rises above the price set in the pending order.
BuyStop is a pending order to buy assets for a security at a price higher than the current one. The order will be executed (modified into market order Buy) if the Ask price reaches or rises above the price set in the pending order.
SellStop is a pending order to sell assets for a security at a price lower than the current one. The order will be executed (modified into market order Sell) if the Bid price reaches or falls below the price set in the pending order.
Lot is the volume of an order expressed in the amount of lots.
StopLoss is a stop order; it is a price set by trader, at which a market order will be closed if the symbol price moves in a direction that produces losses for the order.
TakeProfit is a stop order; it is a price set by trader, at which a market order will be closed if the symbol price moves in a direction that produces profits for the order.

GetLastError()
Symbol()
*/

/*
 types of trades

OP_BUY 	0 	Buy
OP_SELL 	1 	Sell
OP_BUYLIMIT 	2 	Pending order BUY LIMIT
OP_SELLLIMIT 	3 	Pending order SELL LIMIT
OP_BUYSTOP 	4 	Pending order BUY STOP
OP_SELLSTOP 	5 	Pending order SELL STOP
*/

/*
int OrderSend (string symbol, int cmd, double volume, double price, int slippage, double stoploss,
        double takeprofit, string comment=NULL, int magic=0, datetime expiration=0, color arrow_color=CLR_NONE)
OrderSend(Symbol(),OP_BUY,0.1,Ask,3,Bid-15*Point,Bid+15*Point);
*/
int CreateTrade() {
    double Prots = 0.35;

    while (true) {
        // get values
        int market_stop_level = MarketInfo(symbol, MODE_STOPLEVEL);
        //Alert("market stop level = ", market_stop_level);
        double market_lot_min = MarketInfo(symbol, MODE_MINLOT);
        //Alert("market minimum lot size = ", market_lot_min);
        double account_margin_free = AccountFreeMargin();
        //Alert("account margin free = ", account_margin_free);
        double market_margin_required = MarketInfo(symbol, MODE_MARGINREQUIRED);
        //Alert("margin margin required = ", market_margin_required);
        double lot = MathFloor(account_margin_free * Prots * market_margin_required * market_lot_min) * market_lot_min;
        lot = market_lot_min;
        //Alert("lot = ", lot);
        //Alert("Lot: ", lot, " Market Min: ", market_stop_level);

        // get price
        double Price = Bid + ENTRY * Point;
        double PriceMinimum = Ask + market_stop_level * Point;
        if (Price < PriceMinimum) {
            Alert("Entry price too low (", Price, ") changed to ", PriceMinimum);
            Price = PriceMinimum;
        }
        Price = NormalizeDouble(Price, Digits);

         // get stop loss
         double SL = Price - STOP_LOSS * Point;
         if (STOP_LOSS < market_stop_level) {
            SL = Price - market_stop_level * Point;
            Alert("Increased the distance of SL = ", market_stop_level, " pt");
         }

         // get take profit
         double TP = Price + TAKE_PROFIT * Point;
         if (TAKE_PROFIT < market_stop_level) {
             TP = Price + market_stop_level * Point;
             Alert("Increased the distance of TP = ", market_stop_level, " pt");
         }
         
         // get expiration
         datetime expire_at = TimeCurrent() + EXIT_AT * 60;
         //Alert("Exit at ", TimeToStr(expire_at, TIME_SECONDS));

         // entered trade
         Alert("Price: ", Price, " TP: ", TP, " SL: ", SL, " Exit: ", TimeToStr(expire_at, TIME_SECONDS));
         int ticket = OrderSend(symbol, OP_BUYSTOP, lot, Price, 0, SL, TP, NULL, 0, expire_at);

         // success
         if (ticket > 0) {
            Alert("Placed order BuyStop ", ticket);
            break;
         }

         // fail
         int error_code = GetLastError();
         // temp errors
         switch (error_code) {
            case 129:
               Alert("Invalid price. Retrying...");
               RefreshRates();
               continue;
            case 130:
               Alert("The price stops is incorrect. Retrying...");
               RefreshRates();
               continue;
            case 135:
               Alert("The price has changed. Retrying...");
               RefreshRates();
               continue;
            case 146:
               Alert("Trading subsystem is busy. Retrying...");
               Sleep(500);
               RefreshRates();
               continue;
        }
        // perm errors
        switch (error_code) {
            case 2:
               Alert("Common error.");
               break;
            case 5:
               Alert("Outdated version of the client terminal.");
               break;
            case 64:
               Alert("The account is blocked.");
               break;
            case 133:
               Alert("Trading forbidden");
               break;
            default:
               Alert("Occurred error ", error_code);
        }

        break;
    }

    Alert("The script has completed its operations -----------------------------");
    return ticket;
}



/*
Constant 	Value 	Description
ERR_NO_ERROR 	0 	No error returned.
ERR_NO_RESULT 	1 	No error returned, but the result is unknown.
ERR_COMMON_ERROR 	2 	Common error.
ERR_INVALID_TRADE_PARAMETERS 	3 	Invalid trade parameters.
ERR_SERVER_BUSY 	4 	Trade server is busy.
ERR_OLD_VERSION 	5 	Old version of the client terminal.
ERR_NO_CONNECTION 	6 	No connection with trade server.
ERR_NOT_ENOUGH_RIGHTS 	7 	Not enough rights.
ERR_TOO_FREQUENT_REQUESTS 	8 	Too frequent requests.
ERR_MALFUNCTIONAL_TRADE 	9 	Malfunctional trade operation.
ERR_ACCOUNT_DISABLED 	64 	Account disabled.
ERR_INVALID_ACCOUNT 	65 	Invalid account.
ERR_TRADE_TIMEOUT 	128 	Trade timeout.
ERR_INVALID_PRICE 	129 	Invalid price.
ERR_INVALID_STOPS 	130 	Invalid stops.
ERR_INVALID_TRADE_VOLUME 	131 	Invalid trade volume.
ERR_MARKET_CLOSED 	132 	Market is closed.
ERR_TRADE_DISABLED 	133 	Trade is disabled.
ERR_NOT_ENOUGH_MONEY 	134 	Not enough money.
ERR_PRICE_CHANGED 	135 	Price changed.
ERR_OFF_QUOTES 	136 	Off quotes.
ERR_BROKER_BUSY 	137 	Broker is busy.
ERR_REQUOTE 	138 	Requote.
ERR_ORDER_LOCKED 	139 	Order is locked.
ERR_LONG_POSITIONS_ONLY_ALLOWED 	140 	Long positions only allowed.
ERR_TOO_MANY_REQUESTS 	141 	Too many requests.
ERR_TRADE_MODIFY_DENIED 	145 	Modification denied because an order is too close to market.
ERR_TRADE_CONTEXT_BUSY 	146 	Trade context is busy.
ERR_TRADE_EXPIRATION_DENIED 	147 	Expirations are denied by broker.
ERR_TRADE_TOO_MANY_ORDERS 	148 	The amount of opened and pending orders has reached the limit set by a broker.
*/