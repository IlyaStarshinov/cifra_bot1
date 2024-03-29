from email import message
import re
from tracemalloc import start
from turtle import setx
from aiogram import types, executor, Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from requests import request   



TOKEN = "5796328526:AAHwcp2XzN1oJ-G-05RwoughoBZ3PJAbJno"
storage = MemoryStorage()
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=storage)


dep = ['HR','PR','Команда разработчиков']
sx = ['Мужской','Женский']
hob = ['IT','Спорт','Путешествия']
ans = ['Да','Нет']
create = ['/create']

def kb1(items: list[str]) -> ReplyKeyboardMarkup:    

    
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


def get_cancel_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('/cancel'))

    return kb

class QuestionnaireStatesGroup(StatesGroup):
    department = State()
    sex = State()
    age = State()
    hobbies = State()

@dp.message_handler(commands=['cancel'], state='*')
async def cancel_command(message: types.Message, state: FSMContext ):
    if state is None:
        return
    await state.finish()
    await message.answer('Вы прервали создание анкеты!', reply_markup=kb1(create))

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message) -> None:
    await message.answer(f'Привет, {message.chat.first_name} {message.chat.last_name}! Для начала нужно заполнить анкету, для этого нажми /create', reply_markup=kb1(create))

    

@dp.message_handler(commands=['create'])
async def create_command(message: types.Message) -> None:
    await message.answer('Давай же начнем! Для начала выбери свой отдел', reply_markup=kb1(dep))
    await QuestionnaireStatesGroup.department.set()

@dp.message_handler(content_types=['text'], state=QuestionnaireStatesGroup.department)
async def load_department(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['department'] = message.text

    await message.answer('Теперь укажи свой пол',reply_markup=kb1(sx))
    await QuestionnaireStatesGroup.next()

@dp.message_handler(lambda message: not message.text.isdigit(), state=QuestionnaireStatesGroup.age)
async def check_age(message: types.Message):
    await message.answer(f'{message.chat.first_name}, это не число!')


@dp.message_handler(state=QuestionnaireStatesGroup.sex)
async def load_sex(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['sex'] = message.text

    await message.answer('Сколько тебе лет?',reply_markup=types.ReplyKeyboardRemove())
    await QuestionnaireStatesGroup.next()

@dp.message_handler(state=QuestionnaireStatesGroup.age)
async def load_age(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['age'] = message.text

    await message.answer('Теперь укажи своё хобби',reply_markup=kb1(hob))
    await QuestionnaireStatesGroup.next()

@dp.message_handler(state=QuestionnaireStatesGroup.hobbies)
async def load_hobbies(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['hobbies'] = message.text
        await bot.send_message(chat_id=message.from_user.id, text=f"Имя - {message.chat.first_name} {message.chat.last_name}\nОтдел - {data['department']}\nПол - {data['sex']}\nВозраст - {data['age']}\nХобби - {data['hobbies']}")
        await message.answer('Ваша анкета успешно создана!',reply_markup=types.ReplyKeyboardRemove())    
    await state.finish()
        

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
 

