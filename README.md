# Introduction
The Purpose of this analysis is to provide investors a perspective on price as it relates to the previous cycles. 

# Method

## Extract and Load
The data was taken from yfinance and https://www.investing.com/crypto/bitcoin and loaded into SQL database. The data was then loaded to pandas for curation and cleaning.

## Prophet Model

Prophet is specifically designed for business time series prediction. It achieves very good results for the stock data but it can fail on time series datasets from other domains. In particular, this holds for time series where the notion of calendar date is not applicable and we cannot learn any seasonal patterns. Prophet’s advantage is that it requires less hyperparameter tuning as it is specifically designed to detect patterns in business time series. Due to the hyperbolic exponential growth of Bitcoins price and adoption, after 2024, upper/lower/middle bound predictions "fray" - as seen on the bitcoin log price prediction and the bitcoin value prediction.

The process for prophet is to create a df_train, fitting it into a prophet model, and m.predict forecast. The forecast function splits the y value into yhat, yhat_lower and yhat_upper. This creates upper, lower and middle projections. By using m.plot(forecast), the df_train and forecast values are plotted. However, there is another method called insample wherein the analyst can set the pd.date_range of the prediction. Insample was used to predict prices.

## Meanaverage

To calculate Meanaverage, the code below was implemented. This is used as measure of status - over/under valuation of price.

<pre><code>
df['200D'] = df['price'].rolling(200).mean()
df['300D'] = df['price'].rolling(300).mean()
df['50D'] = df['price'].rolling(50).mean()
df = df.dropna()
df['meanavge'] = (df['200D'] + df['300D'] + df['50D'] )/3
df = df.drop(columns=['200D','300D', '50D'])
df['meanvalue'] = df["price"] - df["meanavge"]
df['status'] = df['meanvalue'].apply(lambda x: '1' if x > 0 else '0')
df['status']=df['status'].astype("object")
</code></pre>

## Binning

To calculate standard deviation %, code below was implemented. 

<pre><code>
df['price-meanavge']=df['price'] - df['meanavge']
df['move%'] = df['price-meanavge']/(df['price'] + df['meanavge'])
</code></pre>

<pre><code>
df.describe()

price	meanavge	meanvalue	price-meanavge	move%
count	4138.000000	4138.000000	4138.000000	4138.000000	4138.000000
mean	9317.365684	8866.038283	451.327402	451.327402	0.044424
std	14908.276725	14034.813306	5034.706377	5034.706377	0.173320
min	2.000000	4.964000	-19157.461556	-19157.461556	-0.659858
25%	252.675000	273.201444	-117.995611	-117.995611	-0.077395
50%	1176.650000	897.974083	17.276167	17.276167	0.047788
75%	9932.450000	8685.476486	448.184542	448.184542	0.145141
max	67527.900000	52102.493056	31522.240056	31522.240056	0.706969

bins = [-0.43, -0.1, 0, 0.1, 0.43]
group_names = ["Severely Oversold","Oversold", "Neutral","Overbought"]
df["Valuation"] = pd.cut(df["move%"], bins, labels=group_names)
</code></pre>

## Plotly Graphs

### Approximate Next ATH

The image below shows the length each cycle can reach the previous all time high. The dotted green lines are bitcoin halving dates, the length of period the price has stayed above/below the meanaverage. This graph includes two colors of the price - red for above the meanaverage, and orange - below the meanaverage.
<p align="center">
  <img width="460" height="300" src="static\ApproxnextATH.jpg">
</p>

The image below shows the length, draw ups and draw downs for each cycle. The dotted lines show the the halving dates. The different colors on the lines show the different buy zones as it relates to the standard deviations to the mean. The 3 lines following the price are the middle, upper and lower bounds from the prophet model. 

### Prophet Model and Bull/Bear

<p align="center">
  <img width="460" height="300" src="static\prohetandbullbear.jpg">
</p>

Summary

The Purpose of this analysis is to provide investors a perspective on price as it relates to the previous cycles. Using prior knowledge of previous cycles and plotting them accurately displaying lengths of bull/bear, halving dates, draw ups/downs and buy zones, we can help investors get a better perspective on current technical price conditions and help them allocate capital in a appropriate timely fashion.







