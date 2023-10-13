import asyncio
from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.types import Message
from aiogram.filters import CommandStart
from dotenv import load_dotenv
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import logging
import pandas as pd
import io
import os
import sys
import buttons as kb
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

load_dotenv()
TOKEN = os.getenv("TOKEN")
form_router = Router()
dp = Dispatcher()
bot = Bot(token = TOKEN, parse_mode=ParseMode.HTML)

#БОТ ДЛЯ АНАЛИЗА ФАЙЛА EXCEL С ОЦЕНКАМИ ФГС В ЧАСТНОСТИ ПО ГРУППЕ ПИ101
class Lab(StatesGroup):
    group = State()

@form_router.message(CommandStart())
async def command_start(message: Message):
    await message.answer("Привет! Бот готов приступить к анализу файла Excel! Отправьте файл и <b> ДОЖДИТЕСЬ</b> сообщения о его получении!")

@form_router.message(F.document)
async def get_doc(message: Message):
    doc = message.document.file_id
    print(doc) #получение айди файла, который скинули в бот
    await message.answer('<b>Подождите, файл загружается!</b>')
    file = await bot.get_file(doc)
    file_path = file.file_path
    my_object = io.BytesIO()
    MyBinaryIO = await bot.download_file(file_path, my_object)
    print(MyBinaryIO)

    global df #объявление переменную глобальной, чтобы к ней можно было обращаться и из других функций
    try:
        df = pd.read_excel(MyBinaryIO)
    except ValueError:
        await message.answer(f'ОШИБКА! Формат файла не определен как файл Excel!') #выведет сообщение об ошибке и в терминале
        print('ОШИБКА пользователя: файл НЕ Excel!')
    else:
        print(df)
        await message.answer('Файл получен!', reply_markup=kb.main1)

@form_router.message(F.text == 'Показать список всех групп')
async def report(message: Message):
    columns = list(df.columns.values )
    if 'Группа' and 'Год' and 'Уровень контроля' and 'Личный номер студента' in columns:
        groups = df['Группа'].unique()
        listGroup = ', '.join(groups)
        await message.answer(f'В датасете содержатся оценки следующих групп: {listGroup}', reply_markup=kb.main1)
    else:
        await message.answer(f'ОШИБКА! Файл не может быть обработан из-за ошибки в его структуре!')
        print('ОШИБКА пользователя: нет нужных элементов в структуре таблицы Excel!') #выведет сообщение об ошибке и в терминале

@form_router.message(F.text == 'Выбрать группу')
async def report(message: Message, state: FSMContext) -> None:
    await state.set_state(Lab.group)
    await message.answer("Введите номер группы:", reply_markup=ReplyKeyboardRemove())

@form_router.message(Lab.group)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(group = message.text)
    await message.answer(f'Вы выбрали группу  {html.quote(message.text)}')
    whatGroup = df['Группа'].str.contains(str(message.text)).sum()
    if whatGroup == 0:
        await message.answer(f'Кажется, такой группы нет в данном документе', reply_markup=kb.main1)
        print('ОШИБКА пользователя: выбранной группы НЕТ в полученном документе!') #выведет сообщение об ошибке и в терминале
    else:
        await message.answer(f'Вывести данные о группе: {html.quote(message.text)}?', reply_markup=kb.report1)

@dp.callback_query(F.data == 'otchet')
async def cbquantity(callback: CallbackQuery, state: FSMContext):
    #те же самые переменные, что были у меня в Лаб 1
    group1 = await state.get_data()
    all_marks = df.shape[0]
    count_marks_pi101 = len(df[df['Группа'] == group1['group']])
    count_student_pi101 = df.loc[df['Группа'] == group1['group'], 'Личный номер студента'].nunique()
    mass_id_stud_pi101 = df.loc[df['Группа'] == group1['group'], 'Личный номер студента'].unique()
    id_stud_pi101 = ", ".join(map(str, mass_id_stud_pi101))
    mass_forms_control = df.loc[df['Группа'] == group1['group'], 'Уровень контроля'].unique()
    forms_control = ", ".join(mass_forms_control)
    all_years1 = df.loc[df['Группа'] == group1['group'],'Год'].unique()
    all_years = ", ".join(map(str, all_years1))
    await callback.message.answer(f'В исходном датасете содержалось {all_marks} оценок, из них {count_marks_pi101} относятся к группе {group1}')
    await callback.message.answer(f'В датасете находятся оценки {count_student_pi101} студентов со следующими личными номерами: {id_stud_pi101}')
    await callback.message.answer(f'Используемые формы контроля: {forms_control}')
    await callback.message.answer(f'Данные представлены по следующим учебным годам: {all_years}')
    await callback.message.answer(f'<b><i> Чтобы вывести НОВЫЙ ОТЧЕТ уже ПО ДРУГОЙ ГРУППЕ, воспользуйтесь кнопками </i></b>', reply_markup=kb.main1)

async def main():
    bot = Bot(token = TOKEN, parse_mode=ParseMode.HTML)
    dp.include_router(form_router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())