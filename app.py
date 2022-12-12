from flask import Flask, redirect, render_template, request
import numpy as np
import pandas as pd
from prophet import Prophet
import yfinance as yf



app = Flask(__name__)

@app.route("/")
def view_home():
    return render_template("index.html", title="")
    

@app.route('/run', methods=['GET', 'POST'])
def route():
    print('Inside route')
    # If a form is submitted
    if request.method == "POST":
        df = pd.read_csv("Resources/btcjoin.csv", parse_dates=['date'])
        btc_df = yf.download('BTC-USD')
        btc_df = btc_df.reset_index()
        btc_df = btc_df.loc[(btc_df['Date'] > '2022-10-25')]
        btc_df['Close']=btc_df['Close'].astype("float")
        df['price']=df['price'].str.replace(',','')
        df['price']=df['price'].astype("float")
        btc_df = btc_df.rename(columns={"Close": "price", "Date":"date"})
        df = pd.merge(df, btc_df, on=['date', 'price'], how='outer')
        df = df.drop(columns=['volume','change', 'low', 'high', 'open','Open','High','Low','Adj Close', 'Volume', 'Unnamed: 0'])
        df = df.rename(columns={"value": "wallets"})
        df['priceL'] = np.log(df['price'])

        df = df[['date', 'priceL']]
        df = df.rename(columns = {"date":"ds", "priceL":"y"})
        
        # instantiate the model and set parameters
        model = Prophet()

        # fit the model to historical data
        model.fit(df)

        # # Get values through input bars
        start = "2010-09-25"
        Date = request.form.get("Date")    

        insample = pd.DataFrame(pd.date_range(start, Date, periods=92))
        insample.columns = ['ds']

        # in-sample prediction
        predictionprice = model.predict(insample)

        # Get prediction
        predictionprice = predictionprice[predictionprice['ds'].dt.strftime('%Y-%m-%d') == Date]
        predictionprice = np.exp(predictionprice.yhat)
        predictionprice = predictionprice.values[0].round(2)
        # predictionprice = ("On " +str(Date) + ", the forecasted price of bitcoin is $" + str(predictionprice))

        dfvalue = pd.read_csv("Resources/mlvaluedata.csv")

        # instantiate the model and set parameters
        model = Prophet()

        # fit the model to historical data
        model.fit(dfvalue)

        # in-sample prediction
        predictionvalue = model.predict(insample)

        # Get prediction
        predictionvalue = predictionvalue[predictionvalue['ds'].dt.strftime('%Y-%m-%d') == Date]
        predictionvalue = np.exp(predictionvalue.yhat)
        predictionvalue = predictionvalue.values[0].round(2)
        # predictionvalue = ("The forecasted value of bitcoin is $" + str(predictionvalue))
        predictionvalue
        

        dfwallet = pd.read_csv("Resources/mlwalletsdata.csv")

        # instantiate the model and set parameters
        model = Prophet()

        # fit the model to historical data
        model.fit(dfwallet)

        # in-sample prediction
        predictionwall = model.predict(insample)

        # Get prediction
        predictionwall = predictionwall[predictionwall['ds'].dt.strftime('%Y-%m-%d') == Date]
        predictionwall = (predictionwall.yhat)
        predictionwall = int(predictionwall.values[0])
        # predictionwall = ("The forecasted number of bitcoin wallets are " + str(predictionwall))
      
        df = pd.read_csv("Resources/btcjoin.csv", parse_dates=['date'])
        btc_df = yf.download('BTC-USD')
        btc_df = btc_df.reset_index()
        btc_df = btc_df.loc[(btc_df['Date'] > '2022-10-25')]
        btc_df['Close']=btc_df['Close'].astype("float")
        df['price']=df['price'].str.replace(',','')
        df['price']=df['price'].astype("float")
        btc_df = btc_df.rename(columns={"Close": "price", "Date":"date"})
        df = pd.merge(df, btc_df, on=['date', 'price'], how='outer')
        df = df.rename(columns={"value": "wallets"})
        df = df.drop(columns=['volume','change', 'low', 'high', 'open','Open','High','Low','Adj Close', 'Volume', 'Unnamed: 0', "wallets", "address", "mined"])
        df['200D'] = df['price'].rolling(200).mean()
        df['300D'] = df['price'].rolling(300).mean()
        df['50D'] = df['price'].rolling(50).mean()
        df = df.dropna()
        df['meanavge'] = (df['200D'] + df['300D'] + df['50D'] )/3
        df = df.drop(columns=['200D','300D', '50D'])
        df['meanvalue'] = df["price"] - df["meanavge"]
        df['status'] = df['meanvalue'].apply(lambda x: '1' if x > 0 else '0')
        df['status']=df['status'].astype("object")
        df['price-meanavge']=df['price'] - df['meanavge']
        df['move%'] = df['price-meanavge']/(df['price'] + df['meanavge'])
        bins = [-0.43, -0.1, 0, 0.1, 0.43]
        group_names = ["Severely Oversold","Oversold", "Neutral","Overbought"]
        df["Valuation"] = pd.cut(df["move%"], bins, labels=group_names)
        pricefrommean = df.meanvalue.iloc[-1].round(2)
        currentzone = df.Valuation.iloc[-1]
        # Average length of days price stayed under meanaverage or undervalued/severely oversold
        delta1cycle = df.index[df['date']=='2015-09-15'].tolist()[0] - df.index[df['date']=='2013-12-04'].tolist()[0]
        delta2cycle = df.index[df['date']=='2019-04-2'].tolist()[0] - df.index[df['date']=='2017-12-17'].tolist()[0] 
        averageunder = int((delta1cycle+delta2cycle)/2)
        # Average length of days from previous cycle peak to reach new all time high
        delta1fromp2p = df.index[df['date']=='2017-03-17'].tolist()[0] - df.index[df['date']=='2013-12-04'].tolist()[0]
        delta2fromp2p = df.index[df['date']=='2020-11-29'].tolist()[0] - df.index[df['date']=='2017-12-17'].tolist()[0] 
        averagep2p = int((delta1fromp2p+delta2fromp2p)/2)
        # Days since last all time high
        sincealltimehigh = df.index[-1] - df.index[df['price']==df.price.max()].tolist()[0]

        msg2 = (". The current price from the mean is "  +str(pricefrommean) + ", the average length of days price stayed under meanaverage or undervalued/severely oversold is " + str(averageunder)) + ", the average length of days to reach the previous cycle peak is " + str(averagep2p) + (", and the number of days since last all time high " + str(sincealltimehigh)+ ".")
        
        prediction = ("On " +str(Date) + ", the forecasted price of bitcoin is $" + str(predictionprice)) + (", the value of bitcoin is $" + str(predictionvalue) + (", and the number of bitcoin wallets are " + str(predictionwall) + str(msg2))) 

    else:
        prediction = ""
    return render_template("index.html", output = prediction, date=Date)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=5000)