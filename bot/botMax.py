import aiomax
import time

from aiomax import fsm

from utils import StopWatch, MapStopWatch, User, MapUser, Task

bot = aiomax.Bot("f9LHodD0cOIRY0kxaAAsvfhYqEv2ley3x9B2T7Mn6JIxw7Y6i5U8Wu1eMGbWXUNk1menHVRnTDdwyLRUe6mA",
                 default_format="markdown")




mapStopWatch = MapStopWatch()
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
    b = aiomax.buttons.CallbackButton("Создать секундомер", "create_stopWatch")
    kbStart.add(b)
    await pd.send("POMODORO BOT", keyboard=kbStart)


@bot.on_command('create_stopWatch')
@bot.on_button_callback('create_stopWatch')
async def create_timer(ctx: aiomax.CommandContext):
    global mapStopWatch

    if ctx.user_id in mapStopWatch.stopWatches:
        t = mapStopWatch.get(ctx.user_id)
        await bot.delete_message(str(t.msg_start))
    stopWhatch = StopWatch(ctx.user_id, time.time())

    kbTimer = aiomax.buttons.KeyboardBuilder()
    btn1 = aiomax.buttons.CallbackButton("Запустить секундомер", "start_stopWatch")
    btn2 = aiomax.buttons.CallbackButton("Создать задачу", "create_task")
    kbTimer.add(btn1)
    kbTimer.add(btn2)

    m = await ctx.message.reply(
        f"Секундомер создан. Вы можете запустить его или создать задачу.",
        keyboard=kbTimer
    )
    stopWhatch.add_msg_id(m.id)
    mapStopWatch.add(stopWhatch)


# Отправляем сообщение с кнопкой при вводе команды /start_timer
@bot.on_command('start_stopWatch')
@bot.on_button_callback('start_stopWatch')
async def start_timer(ctx: aiomax.CommandContext):
    global mapStopWatch

    kbTimer = aiomax.buttons.KeyboardBuilder()
    btn1 = aiomax.buttons.CallbackButton("Остановить секундомер", "stop_stopWatch")
    kbTimer.add(btn1)

    timer = mapStopWatch.get(ctx.user_id)
    timer.set_time_start(time.time())

    m = await ctx.message.reply(
        f"Секундомер запущен в {time.localtime().tm_hour}:{'0' if time.localtime().tm_min < 10 else ''}{time.localtime().tm_min}",
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
    btn1 = aiomax.buttons.CallbackButton("Запустить секундомер", "start_stopWatch")
    kbTimer.add(btn1)
    await message.reply(f"Задача {name_of_task} создана, ценность {value_of_task}", keyboard=kbTimer)

    cursor.clear()


@bot.on_button_callback("stop_stopWatch")
async def end_timer(ctx: aiomax.CommandContext):
    global mapStopWatch
    timer = mapStopWatch.get(ctx.user_id)
    await bot.delete_message(str(timer.msg_start))
    timer.time_end = time.time()
    kbEnd = aiomax.buttons.KeyboardBuilder()
    btn1 = aiomax.buttons.CallbackButton("Запустить секундомер", "start_timer")
    btn2 = aiomax.buttons.CallbackButton("Закончить задачу", "end_task")
    kbEnd.add(btn1)
    kbEnd.add(btn2)
    t = time.localtime(time.time() - timer.time_start)
    await ctx.reply(
        f"Время работы: {'0' if t.tm_min < 10 else ''}{t.tm_min}:{'0' if t.tm_sec < 10 else ''}{t.tm_sec}\nСекундомер остановился в {time.localtime().tm_hour}:{'0' if time.localtime().tm_min < 10 else ''}{time.localtime().tm_min}",
        keyboard=kbEnd
    )

@bot.on_button_callback('end_task')
async def end_task(ctx: aiomax.CommandContext):
    global mapStopWatch, mapUser
    timer = mapStopWatch.get(ctx.user_id)
    await bot.delete_message(str(timer.msg_start))
    mapStopWatch.delete(ctx.user_id)
    keyboard = aiomax.buttons.KeyboardBuilder()
    btn1 = aiomax.buttons.CallbackButton("Создать секундомер", "create_timer")
    keyboard.add(btn1)
    user = mapUser.get(ctx.user_id)

    print(user.get_tasks())

    await ctx.reply("Задача завершена. Вы можете создать новый секундомер и задачу", keyboard=keyboard)




if __name__ == "__main__":
    bot.run()
