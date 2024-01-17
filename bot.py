from dotenv import load_dotenv
import os
from typing import Final
import logging                                                            
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, StateFilter
from aiogram import F
import re
from apscheduler.schedulers.asyncio import AsyncIOScheduler


load_dotenv()

TOKEN: Final = os.getenv("TOKEN")
# @NotifyDailyBot
BOT_USERNAME: Final = os.getenv("BOT_USERNAME")

logging.basicConfig(level=logging.INFO)


bot = Bot(token=TOKEN)
dp = Dispatcher()
# initiliazing the reminder
scheduler = AsyncIOScheduler()

# validates user's time input
def is_valid_24h_time(time_str):
    pattern = re.compile(r'^([01]\d|2[0-3]):?([0-5]\d)$')
    return bool(pattern.match(time_str))


@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer('Type /set to start setting a reminder.')

# initializes two states for the dialogue
class SetReminder(StatesGroup):
    choosing_task = State()
    choosing_time = State()


@dp.message(StateFilter(None), Command('set'))
async def task(message: types.Message, state: FSMContext):
    await message.answer('Type the task to remind of:')
    # sets state of choosing a task
    await state.set_state(SetReminder.choosing_task)


@dp.message(SetReminder.choosing_task)
async def time(message: types.Message, state: FSMContext):
    # for the reminder's messaging function
    global chat_id
    chat_id = message.chat.id
    # for the reminder's task
    global reminder_text
    reminder_text = message.text
    await message.answer("Type the time of the reminder in 24h format:")
    # sets state of choosing time
    await state.set_state(SetReminder.choosing_time)

# reminder's messaging function
async def reminder():
    await bot.send_message(chat_id, reminder_text)


@dp.message(SetReminder.choosing_time)
async def end(message: types.Message, state: FSMContext):
    time_input = message.text
    if is_valid_24h_time(time_input):
        time_text = message.text
        await message.answer("The reminder was created!")
        # sets the reminder
        scheduler.add_job(reminder, 'cron', day_of_week='mon-sun', hour=int(time_text[:2]), minute=int(time_text[3:]))
        # clears the states of the dialogue
        await state.clear()
    else:
        await message.answer("Wrong format. Type time, 11:24, for example.")


async def main():
    # activates the reminder
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
