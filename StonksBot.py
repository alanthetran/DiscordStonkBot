import os
import random
import discord
import finnhub
import locale
import json

from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
FIN_TOKEN = os.getenv('FINNHUB_KEY')

configuration = finnhub.Configuration(
    api_key={
        'token': FIN_TOKEN
    }
)

finnhub_client = finnhub.DefaultApi(finnhub.ApiClient(configuration))

locale.setlocale(locale.LC_ALL,'')

bot = commands.Bot(command_prefix = '$')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord')


@bot.command(name='roll_dice', help='Simulates rolling dice.')
async def roll_dice(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

@bot.command(name='flip_coin', help='Simulates flipping a coin. Bull = Head, Bear = Tails')
async def flip_coin(ctx):
    flip = random.randint(0, 1)
    c = "Bull" if flip == 1 else "Bear"
    await ctx.send(c)

@bot.command(name='price', help='<ticker> Price check for quote')
async def price(ctx, ticker):
    ticker = ticker.upper()
    quote = finnhub_client.quote(ticker)
    p = f'__Ticker: {ticker}__\nOpen: {quote.o}\nHigh: {quote.h}\nLow: {quote.l}\nCurrent: {quote.c}\nPrevious Close: {quote.pc}'
    await ctx.send(p)

@bot.command(name='sentiment', help='<ticker> News Sentiment Score, Aggregated from different sources')
async def sentiment(ctx, ticker):
    ticker = ticker.upper()
    score = finnhub_client.news_sentiment(ticker)
    await ctx.send(score)

@bot.command(name='profile', help='Get general information of a company')
async def profile(ctx, ticker):
    ticker = ticker.upper()
    company = finnhub_client.company_profile2(symbol=ticker)
    if(company.market != None):
        mkt_cap = locale.currency(company.market_capitalization,grouping=True)
    prof = f'__{company.name} ({company.ticker})__\n{company.weburl}\nMarket Cap: {mkt_cap}\nShares Outstanding: {company.share_outstanding}\nIndustry: {company.finnhub_industry}'
    await ctx.send(prof)

@bot.command(name='ta', help='<ticker> <1,5,15,30,60,D,W,M> <from:mm/dd/yy> <to:mm/dd/yy> <indicator>"  "$help indicator" to see all supported indicators')
async def ta(ctx, ticker, res, start, end, indicator):
    indicator = indicator.lower()
    print(indicator)
    await ctx.send(indicator)

@bot.command(name='cnews', help='company news, between date YYYY-MM-DD and YYYY-MM-DD up to 1 year past news')
async def cnews(ctx,ticker,start,end):
    res = ''
    ticker = ticker.upper()
    json_arr = finnhub_client.company_news(ticker, _from=start, to=end)
    #json_dict = json.load(json_arr)
    print(json_arr)
    for idx in range(len(json_arr)):
        dt_obj = datetime.fromtimestamp(json_arr[idx].datetime)
        res = f'__{ticker} News__\nDate: {dt_obj}\nSource: {json_arr[idx].source}\nHeadline: {json_arr[idx].headline}\nURL: {json_arr[idx].url} '
        await ctx.send(res)

@bot.command(name='sup_res', help="<ticker> <1,5,15,30,60,D,W,M> Return support and resistance levels ")
async def sup_res(ctx,ticker,res):
    resistance = "Resistances: "
    support = "Supports: "
    ticker = ticker.upper()
    try:
        quote = finnhub_client.quote(ticker)
    except:
        print("")
    if res.isalpha():
        res = res.upper()
    json_str = finnhub_client.support_resistance(ticker,res)
    for price in json_str.levels:
        if price > quote.c:
            resistance = resistance + str(price) + ", "
        else:
            support = support + str(price) + ", "
    await ctx.send("Current: " + str(quote.c) + "\n" + resistance + "\n" + support)

@bot.command(name="ta_sentiment", help="<ticker> <1,5,15,30,60,D,W,M> Get aggregate signal of multiple technical indicators such as MACD, RSI, Moving Average v.v.")
async def ta_sentiment(ctx,ticker,res):
    ticker = ticker.upper()
    if res.isalpha():
        res = res.upper()
    json_str = finnhub_client.aggregate_indicator(ticker,res)
    await ctx.send(json_str)

bot.run(TOKEN)