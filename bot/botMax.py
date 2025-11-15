import aiomax

from interfaces import TaskInterface, StopWatchInterface
import task
import stopWatch

bot = aiomax.Bot("f9LHodD0cOIRY0kxaAAsvfhYqEv2ley3x9B2T7Mn6JIxw7Y6i5U8Wu1eMGbWXUNk1menHVRnTDdwyLRUe6mA",
                 default_format="markdown")


class User:
    id: int
    name: str | None
    points: int
    time_spent: float

    def __init__(self, id: int, name: str = None) -> None:
        self.id = id
        self.name = name
        self.points = 0
        self.tasks = []
        self.time_spent = 0.0

    def add_points(self, points: int) -> None:
        self.points += points

    def add_time_spent(self, time_spent: float) -> None:
        self.time_spent += time_spent

    def get_points(self) -> int:
        return self.points

    def get_time_spent(self) -> float:
        return self.time_spent


class UserStorage:
    users: dict[int: User]

    def __init__(self):
        self.users = {}

    def add(self, user: User) -> None:
        self.users[user.id] = user

    def get(self, id: int) -> User:
        return self.users[id]

    def delete(self, id: int) -> None:
        del self.users[id]


mapUser = UserStorage()


@bot.on_bot_start()
async def startBot(pd: aiomax.BotStartPayload):
    kbStartBot = aiomax.buttons.KeyboardBuilder()
    b = aiomax.buttons.CallbackButton("START", "start")
    kbStartBot.add(b)
    await pd.send(
        "Pomodoro🍅 Бот предназначен для отслеживания своего времени",
        keyboard=kbStartBot
    )


@bot.on_button_callback('start')
@bot.on_command('start')
async def start(ctx: aiomax.CommandContext):
    user_id = ctx.user_id

    user = User(user_id)
    mapUser.add(user)

    kbStart = aiomax.buttons.KeyboardBuilder()
    b1 = aiomax.buttons.CallbackButton("Создать секундомер", StopWatchInterface.create_stopWatch)
    b2 = aiomax.buttons.CallbackButton("Список задач", TaskInterface.list_tasks)
    kbStart.row(b1, b2)
    await ctx.send("POMODORO BOT", keyboard=kbStart)


@bot.on_ready()
async def send_commands():
    await bot.patch_me(commands=[
        aiomax.BotCommand("start", "Старт")
    ])


if __name__ == "__main__":
    bot.add_router(task.router)
    bot.add_router(stopWatch.router)
    bot.run()
