from strategy.dependecies import *

# class MarketOnClosePortfolio(Portfolio):
class MarketOnClosePortfolio():
    """ 
    Here we define our portfolio to keep track of our indicators & strategies

    Return:
    Pandas DataFrame for a set strategy analysis.
    """

    def __init__(self, initial_capital, cap_on_order, inital_num_shares, comission_per_trade, symbol, data, signal_hist):
        # Class Constructor
        # super().__init__()
        self.initial_capital = initial_capital          # Intial Amount of Cash that can be lost (Euros)
        self.inital_num_shares = inital_num_shares      # Initial Amount of Shares (before the start of trading)
        self.cap_on_order = cap_on_order                # Fixed Amount of Cash set to be placed on each trade order
        self.num_share_to_buy = 0.068                   # Fixed Amount of Shares set to be placed on each trade order
        self.comission_per_trade = comission_per_trade  # Comission (%) per trade
        self.symbol = symbol                            # Market Ticker Symbol
        self.signal_hist = signal_hist                  # Signal History DataFrame 
        self.df = data                                  # Target Timeframe based DataFrame for a Trading Period of `X`
        self.positions = self.generate_positions()      # Postiton Signal History DataFrame

    def generate_positions(self):
        # Generate a pandas DataFrame to store quantity held at any “bar” timeframe
        positions = pd.DataFrame(index=self.signal_hist.index).fillna(0.0)
        positions[self.symbol] = 0.068 * self.signal_hist['trade_signal']         # Transact 100 shares on a signal
        
        # DEV
        # print (positions)
        
        return positions

    def backtest_portfolio(self):
        # Create a new DataFrame ‘portfolio’ to store the market value of an open position
        portfolio = self.positions.multiply(self.df['p_open'], axis=0)
        pos_diff = self.positions.diff()

        portfolio.dropna(inplace=True)

        print (portfolio)
        print (pos_diff)

        portfolio['comission ($)'] = (self.df['p_open'] * (self.comission_per_trade / 100)) * self.num_share_to_buy

        # Create a ‘holdings’ Series that totals all open position market values
        # and a ‘cash’ column that stores remaining cash in account
        portfolio['holdings'] = self.positions.multiply(self.df['p_open'], axis=0).sum(axis=1)
        portfolio['cash'] = self.initial_capital - (pos_diff.multiply(self.df['p_open'], axis=0)).sum(axis=1).cumsum()
        
        # Sum up the cash and holdings to create full account ‘equity’, then create the percentage returns
        portfolio['total'] = portfolio['cash'] + portfolio['holdings'] - portfolio['comission ($)'] 
        portfolio['returns'] = portfolio['total'].pct_change()
        portfolio[portfolio.eq(0.00000)] = np.nan

        col_round = ['holdings', 'cash', 'total', 'comission ($)']
        portfolio[col_round] = portfolio[col_round].round(2)
        portfolio = portfolio.round({'returns': 5})
        print(portfolio.tail(50))

        # DEV
        print(portfolio)

        return portfolio

    def backtest_portfolio_v2(self):
        # (Filter) Remove 0.0 'position' values, as they are unecessary for the end analysis result
        self.signal_hist = self.signal_hist[self.signal_hist['position'] != 0.0]
        # Create a new DataFrame ‘portfolio’ to store the market value of an open position
        portfolio = pd.DataFrame(index=self.signal_hist.index).fillna(0.0)

        # Buy Order DataFrame
        buy = self.signal_hist[self.signal_hist.position == 1.0]
        buy['Buy Order Time'] = self.df.open_time
        buy['Buy Price'] =  buy['SMA20']
        buy.reset_index(inplace=True)
        
        # Sell Order DataFrame
        sell = self.signal_hist[self.signal_hist.position == -1.0]
        sell['Sell Order Time'] = self.df.open_time
        sell['Sell Price'] = sell['SMA20']
        sell.reset_index(inplace=True)

        # Using 'concat' because it works with NaN Column Values
        portfolio = pd.concat([buy['Buy Order Time'], 
                                buy['Buy Price'],
                                sell['Sell Order Time'],
                                sell['Sell Price']], axis=1)

        # Place Buy Order at SMA20 Price (Leading Indicator)
        # portfolio['BTC'] = cap_on_order / self.signal_hist.loc[(self.signal_hist['position'] == 1.0)]['SMA20']

        # (Optional) Add `comission` to the portfolio ie: comission per trade in ($) dollars
        portfolio['Comission ($)'] = self.cap_on_order * (2 * self.comission_per_trade / 100)
        # Add `Share Quantity` to Portfolio to View how many Shares I own at the time of the trade
        portfolio['Share Quantity'] = self.cap_on_order / buy['Buy Price']
        # Add `Net Trade` to Portfolio to view the total Net profit/loss
        portfolio['total_net'] = self.cap_on_order / (sell['Sell Price'] - buy['Buy Price'] - portfolio['Comission ($)'])
        # Add `Percentage Change`
        portfolio['(%) Change'] = portfolio['total_net'] / buy['Buy Price'] * 100
        # Add `Portfolio Total` to Portfolio
        portfolio['Portfolio Total'] = (self.initial_capital - portfolio['Comission ($)'])
        # Add `Available Cash` to Portfolio
        portfolio['Available Cash ($)'] = self.initial_capital - (portfolio['Share Quantity'] *  portfolio['Sell Price'])

        # Dataframe Options and Filters
        portfolio.reset_index(inplace=True)
        portfolio.fillna(method='ffill', inplace=True)

        # DEV
        # print(portfolio)

        return portfolio

    def backtest_portfolio_v3(self):

        # FIXME: Fic the "Available Cash ($)" column data values and conditions

        # (Filter) Remove 0.0 'position' values, as they are unecessary for the end analysis result
        self.signal_hist = self.signal_hist[self.signal_hist['position'] != 0.0]
        # Create a new DataFrame ‘portfolio’ to store the market value of an open position
        portfolio = pd.DataFrame(index=self.signal_hist.index).fillna(0.0)
        share_diff = self.positions.diff()

        # print(share_diff)
        
        # Buy Order DataFrame
        buy = self.signal_hist[self.signal_hist.position == 1.0]
        buy['Buy Order Time'] = self.df.open_time
        buy['Buy Price'] = buy['SMA20']
        buy['Available Cash ($)'] = self.initial_capital - (share_diff.multiply(buy['Buy Price'], axis=0)).sum(axis=1)
        buy['Holdings ($)'] = (self.positions.multiply(buy['Buy Price'], axis=0)).sum(axis=1)
        buy['Share Quantity'] = self.positions
        buy.reset_index(inplace=True)

        # Sell Order DataFrame
        sell = self.signal_hist[self.signal_hist.position == -1.0]
        sell['Sell Order Time'] = self.df.open_time
        sell['Sell Price'] = sell['SMA20']
        sell['Return Cash ($)'] = - (share_diff.multiply(sell['Sell Price'], axis=0)).sum(axis=1)
        sell.reset_index(inplace=True)

        # Using 'concat' because it works with NaN Column Values
        portfolio = pd.concat([buy['Available Cash ($)'],
                                buy['Buy Order Time'], 
                                buy['Buy Price'],
                                buy['Holdings ($)'],
                                buy['Share Quantity'],
                                sell['Sell Order Time'],
                                sell['Sell Price'],
                                sell['Return Cash ($)']], axis=1)

        # Add `Percentage Change`
        portfolio['(%) Change'] = (portfolio['Return Cash ($)'] - portfolio['Holdings ($)']) / portfolio['Holdings ($)'] * 100
        # portfolio['Running Total'] = (portfolio['Available Cash ($)'] + (portfolio['Available Cash ($)'] * (portfolio['(%) Change'] * 100)))
       
        # (Optional) Add `comission` to the portfolio ie: comission per trade in ($) dollars
        portfolio['Comission ($)'] = (portfolio['Holdings ($)'] + portfolio['Return Cash ($)']) * (self.comission_per_trade / 100)

        # Dataframe Options and Filters
        portfolio.fillna(method='ffill', inplace=True)

        # DEV
        # print(portfolio)

        return portfolio