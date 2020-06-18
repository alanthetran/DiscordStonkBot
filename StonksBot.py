import os
import random
import discord
import finnhub
import locale

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
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
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

@bot.command(name='flip_coin', help='Simulates flipping a coin. Bull = Head, Bear = Tails')
async def flip(ctx):
    flip = random.randint(0, 1)
    c = "Bull" if flip == 1 else "Bear"
    await ctx.send(c)

@bot.command(name='price', help='Price check for quote')
async def price(ctx, ticker):
    ticker = ticker.upper()
    quote = finnhub_client.quote(ticker)
    p = f'__Ticker: {ticker}__\nOpen: {quote.o}\nHigh: {quote.h}\nLow: {quote.l}\nCurrent: {quote.c}\nPrevious Close: {quote.pc}'
    await ctx.send(p)

@bot.command(name='sentiment', help='News Sentiment Score, Aggregated from different sources')
async def sentiment(ctx, ticker):
    ticker = ticker.upper()
    score = finnhub_client.news_sentiment(ticker)
    await ctx.send(score)

@bot.command(name='profile', help='Get general information of a company')
async def profile(ctx, ticker):
    ticker = ticker.upper()
    company = finnhub_client.company_profile2(symbol=ticker)
    mkt_cap = locale.currency(company.market_capitalization,grouping=True)
    prof = f'__{company.name} ({company.ticker})__\n{company.weburl}\nMarket Cap: {mkt_cap}\nShares Outstanding: {company.share_outstanding}\nIndustry: {company.finnhub_industry}'
    await ctx.send(prof)

@bot.command(name='ta', help='"$ta [ticker] ["1,5,15,30,60,D,W,M"] [from:mm/dd/yy] [to:mm/dd/yy] [indicator]"  "$help indicator" to see all supported indicators"')
async def ta(ctx, ticker, res, start, end, indicator):
    indicator = indicator.lower()
    print(indicator)
    await ctx.send(indicator)


bot.run(TOKEN)