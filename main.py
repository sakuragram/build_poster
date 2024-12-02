import asyncio
import os
import subprocess
from datetime import datetime
from time import sleep
from zipfile import ZipFile, ZIP_DEFLATED

from telebot.async_telebot import AsyncTeleBot
import aiohttp
from telebot.types import InputFile

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
        try:
            await bot.reply_to(message, 'Введите список изменений:')
            bot.register_message_handler(set_changelog, content_types=['text'])
        except Exception as e:
            await bot.reply_to(message, f'An error occurred: {e}')
            delete = await bot.send_message(config.channel_id, f'An error occurred: {e}')
            sleep(5)
            await bot.delete_message(config.channel_id, delete.id)


async def set_changelog(message):
    if message.from_user.id == config.developer_id:
        message_for_edit = await bot.send_message(config.channel_id, 'Подготовка...')
        await bot.reply_to(message,
                           f'<a href="https://t.me/sgbuild/{message_for_edit.message_id}">Сборка уже публикуется в канале!</a>'
                           , parse_mode='HTML')
        await build_and_archive_solution(message_for_edit, 'Debug', config.solution_file, caption=message.text)
        pass


async def build_and_archive_solution(message, configuration, solution_path, archive_name='sakuragram.zip', caption=None):
    await bot.edit_message_text('Сборка...', message.chat.id, message.message_id)
    msbuild_command = f'msbuild "{solution_path}" /t:Build /p:Configuration={configuration} /p:Platform=x64 /m /fl /flp:logfile=MyBuildLog.txt;verbosity=detailed /p:OutputPath="{config.build_output}/{configuration}"'
    subprocess.run(msbuild_command, shell=True, check=True)

    await bot.edit_message_text('Архивация...', message.chat.id, message.message_id)
    archive_path = os.path.join(config.build_output, configuration, archive_name)

    with ZipFile(archive_path, 'w', compression=ZIP_DEFLATED, compresslevel=9) as zip_file:
        output_path = os.path.join(config.build_output, configuration)
        for root, dirs, files in os.walk(output_path):
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, output_path)

                if not relative_path.startswith(archive_name):
                    zip_file.write(full_path, arcname=relative_path)
    await bot.edit_message_text('Отправка...', message.chat.id, message.message_id)
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    await bot.send_document(config.channel_id, InputFile(open(archive_path, 'rb'),
                                                         f"sakuragram_Windows_{configuration}_{current_time}.zip"),
                            caption=caption)
    await bot.delete_message(config.channel_id, message.message_id)


if __name__ == '__main__':
    print('Bot is running...')
    asyncio.run(bot.send_message(config.developer_id, 'Бот работает.'))
    asyncio.run(bot.polling())
    print('Bot stopped.')
    asyncio.run(bot.send_message(config.developer_id, 'Бот остановлен.'))
