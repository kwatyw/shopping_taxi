from aiogram import Bot, Dispatcher
from TGBOT import TOKEN_NAME
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from KEYBOARD import *

bot = Bot(token=TOKEN_NAME)
dp = Dispatcher()

CREATOR_ID = [1974703792]
ADMIN_IDS = [1974703792]
SHOPS_IDS = {555585819: 'Ashan', 1928100321: 'Rolex'}
QUERY_ADMIN = []
QUERY_TEMPLATE_ANSWER = {
    "message_id": None,
    "message_text": "",
    "output_str": []
}
QUERY_ANSWERS = []
QUERY_ANSWER_PHOTO = []


def start_load_admins(filename="admins.txt"):
    file = open(filename)
    for line in file.readlines():
        if line == '' or line == '\n':
            continue
        line = int(line.rstrip())
        ADMIN_IDS.append(line)
    file.close()


def start_load_shops(filename="shops.txt"):
    file = open(filename)
    for line in file.readlines():
        if line == '' or line == '\n':
            continue
        line = line.rstrip().split()
        id = int(line[0])
        shop_name = line[1]
        SHOPS_IDS[id] = shop_name
    file.close()


start_load_admins()
start_load_shops()


def load_admin(message: Message):  # /load 129131207
    return message.from_user.id in CREATOR_ID and "/load_admin" in message.text


def load_shops(message: Message):
    return message.from_user.id in ADMIN_IDS and "/load_shop" in message.text


def admin_filter(message: Message):
    return message.from_user.id in ADMIN_IDS


def callback_shop_filter(callback: CallbackQuery):
    return callback.from_user.id in SHOPS_IDS


def indx_by_message_id(query_answers: list[dict], callback_message_id: str):
    lst_ids = [x['message_id'] for x in query_answers]
    for i in range(len(lst_ids)):
        if lst_ids[i] == callback_message_id:
            return i
    return -2


def indx_by_message_text(query_answers: list[dict], message_text: str):
    lst_ids = [x['message_text'] for x in query_answers]
    for i in range(len(lst_ids)):
        if lst_ids[i] == message_text:
            return i
    return -2


@dp.message(Command(commands=['start']))
async def start(message: Message):
    if message.from_user.id in SHOPS_IDS:
        print(message.from_user.id, type(message.from_user.id))
        await message.answer(text=f"Здравствуйте, продавец магазина {SHOPS_IDS[message.from_user.id]}")
    elif message.from_user.id in ADMIN_IDS:
        print(message.from_user.id, type(message.from_user.id))
        await message.answer(text=f"Здравствуйте, администратор")
    else:
        print(message.from_user.id, type(message.from_user.id))
        await message.answer(text="Извините, данный чат-бот только для авторизованных пользователей...")


async def process_load_admin(message: Message):
    lst = message.text.replace(" ", " \n ").split(" ")
    if len(lst) < 2:
        await message.answer("Ошибка! Введите ID пользователя")
    else:
        lst.pop(0)
        file = open("admins.txt", "a")
        file.writelines(lst[:])
        while "\n" in lst:
            lst.remove("\n")
        lst = list(map(int, lst))
        ADMIN_IDS.extend(lst[:])
        file.close()
        await message.answer("Все успешно, пользователи загружены в группу администраторов")


@dp.message(load_shops)
async def process_load_shops(message: Message):
    lst = message.text.replace("/load_shop ", "").split(",")
    lst = list(map(str.strip, lst))
    if len(lst) < 2:
        await message.answer("Ошибка! Введите ID пользователя")
    else:
        file = open("shops.txt", "a")
        for line in lst:
            id, shop_name = int(line[0]), line[1]
            SHOPS_IDS[id] = shop_name
            line += "\n"
            file.write(line)
        file.close()


@dp.message(admin_filter)
async def process_admin_query(message: Message):
    await message.answer("Запрос обрабатывается...", reply_markup=kb_builder_refresh.as_markup(resize_keyboard=True))
    QUERY_ADMIN.append(message.from_user.id)
    QUERY_ANSWERS.append(QUERY_TEMPLATE_ANSWER.copy())
    QUERY_ANSWERS[-1]["message_id"] = message.message_id
    QUERY_ANSWERS[-1]["message_text"] = message.text
    QUERY_ANSWERS[-1]['output_str'] = []
    for i in SHOPS_IDS:
        await bot.send_message(i, message.text, reply_markup=kb_builder.as_markup(resize_keyboard=True))


@dp.callback_query(callback_shop_filter)
async def process_shop_answer(callback: CallbackQuery):
    if callback.data == 'yes':
        answer = f'У магазина {SHOPS_IDS[callback.from_user.id]} есть товар: {callback.message.text}\n'
        indx = indx_by_message_text(QUERY_ANSWERS, callback.message.text)
        if indx != 2:
            QUERY_ANSWERS[indx]['output_str'].append(answer)
    elif callback.data == 'yes_with_photo':
        answer_photo = f'У магазина {SHOPS_IDS[callback.from_user.id]} есть товар: {callback.message.text}\n'
        indx = indx_by_message_text(QUERY_ANSWERS, callback.message.text)
        if indx != -2:
            QUERY_ANSWERS[indx]['output_str'].append(answer_photo)
        QUERY_ANSWER_PHOTO.append(answer_photo)
    if QUERY_ADMIN and callback.data != "yes_with_photo":
        QUERY_ADMIN.pop()
    await callback.message.edit_text(text="Спасибо!")
    await callback.answer()


@dp.callback_query(lambda callback: callback.data == 'refresh')
async def process_shop_answer(callback: CallbackQuery):
    indx = indx_by_message_id(QUERY_ANSWERS, callback.message.message_id - 1)
    if indx != -2:
        await callback.message.edit_text(text=f"{' '.join(QUERY_ANSWERS[indx]['output_str'])}", reply_markup=kb_builder_refresh.as_markup(resize_keyboard=True))
        QUERY_ANSWERS.pop(indx)
    await callback.answer()


@dp.message(lambda message: message.photo)
async def handle_photo(message: Message):
    await bot.download(message.photo[-1].file_id)
    await bot.send_photo(chat_id=QUERY_ADMIN[0], photo=message.photo[-1].file_id, caption=QUERY_ANSWER_PHOTO[0])
    QUERY_ANSWER_PHOTO.pop()
    QUERY_ADMIN.pop()


dp.run_polling(bot)