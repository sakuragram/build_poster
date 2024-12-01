﻿import asyncio

from telebot.async_telebot import AsyncTeleBot
import aiohttp

import config

bot = AsyncTeleBot(token=config.token)

@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    await bot.reply_to(message, 'Hello!')

@bot.message_handler(commands=['stop'])
async def stop_bot(message):
    if message.from_user.id == config.developer_id:
        await bot.reply_to(message, 'Bot is stopping...')
        await bot.close_session()

@bot.message_handler(commands=['post'])
async def post_message(message):
    if message.from_user.id == config.developer_id:
        pass

if __name__ == '__main__':
    print('Bot is running...')
    asyncio.run(bot.send_message(config.developer_id, 'Bot is running...'))
    asyncio.run(bot.polling())
    print('Bot stopped.')
    asyncio.run(bot.send_message(config.developer_id, 'Bot stopped.'))