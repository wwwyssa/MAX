import aiomax
import time

bot = aiomax.Bot("f9LHodD0cOIRY0kxaAAsvfhYqEv2ley3x9B2T7Mn6JIxw7Y6i5U8Wu1eMGbWXUNk1menHVRnTDdwyLRUe6mA",
                 default_format="markdown")


class Timer:
    id: int
    time_start: float
    time_end: float
    msg_start: int

    def __init__(self, id: int, time_start: float, msg_id: int = None) -> None:
        self.id = id
        self.time_start = time_start
        self.msg_start = msg_id

    def add_msg_id(self, msg_id) -> None:
        self.msg_start = msg_id


class MapTimer:
    timers: dict[int: Timer]

    def __init__(self):
        self.timers = {}

    def add(self, timer: Timer) -> None:
        self.timers[timer.id] = timer

    def get(self, id: int) -> Timer:
        return self.timers[id]

    def delete(self, id: int) -> None:
        del self.timers[id]


mapTimer = MapTimer()


@bot.on_bot_start()
@bot.on_command('start')
async def start(pd: aiomax.BotStartPayload):
    kbStart = aiomax.buttons.KeyboardBuilder()
    b = aiomax.buttons.CallbackButton("Start Timer", "start_timer")
    kbStart.add(b)
    await pd.send("POMODORO BOT", keyboard=kbStart)


# Отправляем сообщение с кнопкой при вводе команды /tap
@bot.on_command('start_timer')
@bot.on_button_callback('start_timer')
async def start_timer(ctx: aiomax.CommandContext):
    global mapTimer

    if ctx.user_id in mapTimer.timers:
        t = mapTimer.get(ctx.user_id)
        await bot.delete_message(str(t.msg_start))

    timer = Timer(ctx.user_id, time.time())

    kbTimer = aiomax.buttons.KeyboardBuilder()
    b = aiomax.buttons.CallbackButton("End Timer", "end_timer")
    kbTimer.add(b)
    m = await ctx.message.reply(
        f"Timer Start at {time.localtime().tm_hour}:{'0' if time.localtime().tm_min < 10 else ''}{time.localtime().tm_min}",
        keyboard=kbTimer
    )
    timer.add_msg_id(m.id)
    mapTimer.add(timer)


@bot.on_button_callback("end_timer")
async def end_timer(ctx: aiomax.CommandContext):
    global mapTimer
    timer = mapTimer.get(ctx.user_id)
    await bot.delete_message(str(timer.msg_start))
    timer.time_end = time.time()

    kbEnd = aiomax.buttons.KeyboardBuilder()
    b = aiomax.buttons.CallbackButton("Start Timer", "start_timer")
    kbEnd.add(b)
    t = time.localtime(time.time() - timer.time_start)
    mapTimer.delete(ctx.user_id)
    await ctx.reply(
        f"Concentrate Time: {'0' if t.tm_min < 10 else ''}{t.tm_min}:{'0' if t.tm_sec < 10 else ''}{t.tm_sec}\nTimer End at {time.localtime().tm_hour}:{'0' if time.localtime().tm_min < 10 else ''}{time.localtime().tm_min}",
        keyboard=kbEnd
    )


if __name__ == "__main__":
    bot.run()
