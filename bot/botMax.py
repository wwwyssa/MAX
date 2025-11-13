import aiomax
import time

from aiomax import fsm

from utils import Timer, MapTimer, User, MapUser, Task

bot = aiomax.Bot("f9LHodD0cOIRY0kxaAAsvfhYqEv2ley3x9B2T7Mn6JIxw7Y6i5U8Wu1eMGbWXUNk1menHVRnTDdwyLRUe6mA",
                 default_format="markdown")




mapTimer = MapTimer()
mapUser = MapUser()

@bot.on_bot_start()
@bot.on_command('start')
async def start(pd: aiomax.BotStartPayload):
    global mapUser
    user_name = None
    if type(pd) == aiomax.BotStartPayload:
        user_name = pd.user.name
    else:
        user_name = pd.sender.name
    user_id = pd.user_id

    user = User(user_id, user_name)
    mapUser.add(user)

    kbStart = aiomax.buttons.KeyboardBuilder()
    b = aiomax.buttons.CallbackButton("Создать таймер", "create_timer")
    kbStart.add(b)
    await pd.send("POMODORO BOT", keyboard=kbStart)


@bot.on_command('create_timer')
@bot.on_button_callback('create_timer')
async def create_timer(ctx: aiomax.CommandContext):
    global mapTimer

    if ctx.user_id in mapTimer.timers:
        t = mapTimer.get(ctx.user_id)
        await bot.delete_message(str(t.msg_start))
    timer = Timer(ctx.user_id, time.time())

    kbTimer = aiomax.buttons.KeyboardBuilder()
    btn1 = aiomax.buttons.CallbackButton("Запустить таймер", "start_timer")
    btn2 = aiomax.buttons.CallbackButton("Создать задачу", "create_task")
    kbTimer.add(btn1)
    kbTimer.add(btn2)

    m = await ctx.message.reply(
        f"Таймер создан. Вы можете запустить его или создать задачу.",
        keyboard=kbTimer
    )
    timer.add_msg_id(m.id)
    mapTimer.add(timer)


# Отправляем сообщение с кнопкой при вводе команды /start_timer
@bot.on_command('start_timer')
@bot.on_button_callback('start_timer')
async def start_timer(ctx: aiomax.CommandContext):
    global mapTimer

    kbTimer = aiomax.buttons.KeyboardBuilder()
    btn1 = aiomax.buttons.CallbackButton("Остановить таймер", "stop_timer")
    kbTimer.add(btn1)

    timer = mapTimer.get(ctx.user_id)
    timer.set_time_start(time.time())

    m = await ctx.message.reply(
        f"Таймер запущен в {time.localtime().tm_hour}:{'0' if time.localtime().tm_min < 10 else ''}{time.localtime().tm_min}",
        keyboard=kbTimer
    )


@bot.on_button_callback('create_task')
async def create_task(message: aiomax.Message, cursor: fsm.FSMCursor):
    await message.send("Введите название задачи")
    cursor.change_state('name_of_task')


@bot.on_message(aiomax.filters.state('name_of_task'))
async def write_name(message: aiomax.Message, cursor: fsm.FSMCursor):
    await message.reply("Введите ценность задачи (1-10)")

    cursor.change_state('enter_value')
    cursor.change_data({'name_of_task': message.content})

@bot.on_message(aiomax.filters.state('enter_value'))
async def write_name(message: aiomax.Message, cursor: fsm.FSMCursor):
    global mapUser
    name_of_task = cursor.get_data()['name_of_task']
    if (not message.content.isdigit()) or (int(message.content) < 1) or (int(message.content) > 10):
        await message.reply("Ошибка ввода. Введите ценность задачи (1-10)")
        return
    value_of_task = int(message.content)
    task = Task(name_of_task, value_of_task)

    user = mapUser.get(message.user_id)
    user.add_task(task)


    kbTimer = aiomax.buttons.KeyboardBuilder()
    btn1 = aiomax.buttons.CallbackButton("Запустить таймер", "start_timer")
    kbTimer.add(btn1)
    await message.reply(f"Задача {name_of_task} создана, ценность {value_of_task}", keyboard=kbTimer)

    cursor.clear()


@bot.on_button_callback("stop_timer")
async def end_timer(ctx: aiomax.CommandContext):
    global mapTimer
    timer = mapTimer.get(ctx.user_id)
    await bot.delete_message(str(timer.msg_start))
    timer.time_end = time.time()
    kbEnd = aiomax.buttons.KeyboardBuilder()
    btn1 = aiomax.buttons.CallbackButton("Запустить таймер", "start_timer")
    btn2 = aiomax.buttons.CallbackButton("Закончить задачу", "end_task")
    kbEnd.add(btn1)
    kbEnd.add(btn2)
    t = time.localtime(time.time() - timer.time_start)
    await ctx.reply(
        f"Время работы: {'0' if t.tm_min < 10 else ''}{t.tm_min}:{'0' if t.tm_sec < 10 else ''}{t.tm_sec}\nТаймер остановился в {time.localtime().tm_hour}:{'0' if time.localtime().tm_min < 10 else ''}{time.localtime().tm_min}",
        keyboard=kbEnd
    )

@bot.on_button_callback('end_task')
async def end_task(ctx: aiomax.CommandContext):
    global mapTimer, mapUser
    timer = mapTimer.get(ctx.user_id)
    await bot.delete_message(str(timer.msg_start))
    mapTimer.delete(ctx.user_id)
    keyboard = aiomax.buttons.KeyboardBuilder()
    btn1 = aiomax.buttons.CallbackButton("Создать таймер", "create_timer")
    keyboard.add(btn1)
    user = mapUser.get(ctx.user_id)

    print(user.get_tasks())

    await ctx.reply("Задача завершена. Вы можете создать новый таймер и задачу", keyboard=keyboard)


if __name__ == "__main__":
    bot.run()
