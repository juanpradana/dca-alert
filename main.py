import pandas as pd
import talib
import telegram
import asyncio
import certifi
from binance.client import Client
from datetime import datetime
import logging
from dotenv import load_dotenv
import os
import pytz

# Load environment variables
load_dotenv()

# Konfigurasi logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Konfigurasi Binance API
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

# Konfigurasi Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Parameter strategi
RSI_BUY_THRESHOLD = 30  # Renamed from RSI_THRESHOLD
RSI_SELL_THRESHOLD = 80  # New parameter for sell signals
DCA_LEVELS = 3
DCA_PERCENTAGE = 5.0
SYMBOLS = ['BTCUSDT', 'PAXGUSDT']  # Multiple symbols to monitor
INTERVAL = Client.KLINE_INTERVAL_4HOUR  # Interval 4 jam, bisa disesuaikan

# Inisialisasi client Binance dengan proper SSL verification
client = Client(API_KEY, API_SECRET, {"verify": certifi.where()})

# Inisialisasi bot Telegram
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

def get_binance_data(symbol, interval, limit=100):
    """Mengambil data harga dari Binance"""
    try:
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 
                                           'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
                                           'taker_buy_quote_asset_volume', 'ignore'])
        
        # Konversi tipe data
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('Asia/Jakarta')
        data['close'] = data['close'].astype(float)
        data['high'] = data['high'].astype(float)
        data['low'] = data['low'].astype(float)
        data['open'] = data['open'].astype(float)
        
        return data
    except Exception as e:
        logger.error(f"Error mengambil data dari Binance: {e}")
        return None

def calculate_indicators(data):
    """Menghitung indikator-indikator yang diperlukan"""
    if data is None or len(data) < 50:
        return None
    
    # Menghitung EMA
    data['ema7'] = talib.EMA(data['close'].values, timeperiod=7)
    data['ema14'] = talib.EMA(data['close'].values, timeperiod=14)
    data['ema50'] = talib.EMA(data['close'].values, timeperiod=50)
    
    # Menghitung RSI
    data['rsi'] = talib.RSI(data['close'].values, timeperiod=14)
    
    # Menghitung ATR (volatilitas)
    data['atr'] = talib.ATR(data['high'].values, data['low'].values, data['close'].values, timeperiod=14)
    data['volatility_factor'] = data['atr'] / data['close'] * 100
    
    return data

def check_conditions(data):
    """Memeriksa kondisi untuk sinyal masuk dan keluar"""
    if data is None or data.empty:
        return False, None, None
    
    # Ambil data terbaru
    latest = data.iloc[-1]
    
    # Periksa kondisi buy
    buy_condition = (latest['close'] < latest['ema7'] and 
                    latest['close'] < latest['ema14'] and 
                    latest['rsi'] < RSI_BUY_THRESHOLD)
    
    # Periksa kondisi sell
    sell_condition = (latest['close'] > latest['ema7'] and 
                     latest['close'] > latest['ema14'] and 
                     latest['rsi'] > RSI_SELL_THRESHOLD)
    
    # Buat informasi detail
    price_info = {
        'entry_price': latest['close'],
        'ema7': latest['ema7'],
        'ema14': latest['ema14'],
        'rsi': latest['rsi'],
        'volatility': latest['volatility_factor']
    }
    
    if buy_condition:
        # Tambah level DCA untuk sinyal buy
        dca_prices = []
        for i in range(DCA_LEVELS):
            dca_price = latest['close'] * (1 - i * DCA_PERCENTAGE / 100)
            dca_prices.append(dca_price)
        price_info['dca_levels'] = dca_prices
        return True, False, price_info
    
    if sell_condition:
        return False, True, price_info
    
    return False, False, None

async def send_telegram_buy_alert(price_info):
    """Mengirim alert buy ke Telegram"""
    try:
        # Set timezone ke UTC+7 (Asia/Jakarta)
        tz = pytz.timezone('Asia/Jakarta')
        current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        symbol = price_info['symbol']
        
        message = f"🚨 *{symbol} DCA Buy Signal* 🚨\n\n"
        message += f"*Waktu (UTC+7):* {current_time}\n"
        message += f"*Symbol:* {symbol}\n"
        message += f"*Timeframe:* 4 Jam\n\n"
        
        message += f"*Entry Price:* {price_info['entry_price']:.2f}\n"
        message += f"*EMA7:* {price_info['ema7']:.2f}\n"
        message += f"*EMA14:* {price_info['ema14']:.2f}\n"
        message += f"*RSI:* {price_info['rsi']:.2f}\n"
        message += f"*Volatility:* {price_info['volatility']:.2f}%\n\n"
        
        message += "*DCA Levels:*\n"
        for i, price in enumerate(price_info['dca_levels']):
            message += f"Level {i+1}: {price:.2f}\n"
        
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
        logger.info(f"Alert buy berhasil dikirim ke Telegram untuk {symbol}")
        
    except Exception as e:
        logger.error(f"Error mengirim alert buy ke Telegram: {e}")

async def send_telegram_sell_alert(price_info):
    """Mengirim alert sell ke Telegram"""
    try:
        # Set timezone ke UTC+7 (Asia/Jakarta)
        tz = pytz.timezone('Asia/Jakarta')
        current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        symbol = price_info['symbol']
        
        message = f"💰 *{symbol} SELL Signal* 💰\n\n"
        message += f"*Waktu (UTC+7):* {current_time}\n"
        message += f"*Symbol:* {symbol}\n"
        message += f"*Timeframe:* 4 Jam\n\n"
        
        message += f"*Current Price:* {price_info['entry_price']:.2f}\n"
        message += f"*EMA7:* {price_info['ema7']:.2f}\n"
        message += f"*EMA14:* {price_info['ema14']:.2f}\n"
        message += f"*RSI:* {price_info['rsi']:.2f}\n"
        message += f"*Volatility:* {price_info['volatility']:.2f}%\n"
        
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
        logger.info(f"Alert sell berhasil dikirim ke Telegram untuk {symbol}")
        
    except Exception as e:
        logger.error(f"Error mengirim alert sell ke Telegram: {e}")

async def main():
    """Fungsi utama program"""
    logger.info("Program Crypto DCA Alert dimulai")
    
    # Simpan waktu terakhir alert untuk setiap simbol (terpisah untuk buy dan sell)
    last_buy_alert_times = {symbol: None for symbol in SYMBOLS}
    last_sell_alert_times = {symbol: None for symbol in SYMBOLS}
    
    while True:
        try:
            for symbol in SYMBOLS:
                # Ambil data dari Binance
                data = get_binance_data(symbol, INTERVAL)
                
                # Hitung indikator
                data_with_indicators = calculate_indicators(data)
                
                # Periksa kondisi (buy dan sell)
                buy_triggered, sell_triggered, price_info = check_conditions(data_with_indicators)
                
                current_time = datetime.now()
                
                # Handle buy signal
                if buy_triggered and (last_buy_alert_times[symbol] is None or 
                                    (current_time - last_buy_alert_times[symbol]).seconds > 3600):
                    if price_info:
                        price_info['symbol'] = symbol
                        await send_telegram_buy_alert(price_info)
                        last_buy_alert_times[symbol] = current_time
                
                # Handle sell signal
                if sell_triggered and (last_sell_alert_times[symbol] is None or 
                                     (current_time - last_sell_alert_times[symbol]).seconds > 3600):
                    if price_info:
                        price_info['symbol'] = symbol
                        await send_telegram_sell_alert(price_info)
                        last_sell_alert_times[symbol] = current_time
            
            # Tunggu 5 menit sebelum memeriksa lagi
            logger.info("Menunggu 5 menit untuk pemeriksaan berikutnya...")
            await asyncio.sleep(300)
            
        except Exception as e:
            logger.error(f"Error dalam loop utama: {e}")
            await asyncio.sleep(60)  # Tunggu 1 menit jika terjadi error

if __name__ == "__main__":
    asyncio.run(main())
