import aiomax
import time
from task import Task
from interfaces import TaskInterface, StopWatchInterface
from aiomax import fsm


class StopWatch:
    id: int
    time_start: float
    time_end: float
    msg_start: int
    task: Task

    def __init__(self, id: int, time_start: float, msg_id: int = None) -> None:
        self.id = id
        self.time_start = time_start
        self.msg_start = msg_id
        self.task = None

    def setTimeStart(self, time_start: float) -> None:
        self.time_start = time_start

    def addMsgId(self, msg_id) -> None:
        self.msg_start = msg_id

    def addTask(self, task: Task) -> None:
        self.task = task


class StopWatchStorage:
    stopWatchStorage: dict[int: StopWatch]

    def __init__(self):
        self.stopWatchStorage = {}

    def add(self, stopWatch: StopWatch) -> None:
        self.stopWatchStorage[stopWatch.id] = stopWatch

    def get(self, id: int) -> StopWatch:
        return self.stopWatchStorage[id]

    def delete(self, id: int) -> None:
        del self.stopWatchStorage[id]


router = aiomax.Router()
stopWatchStorage = StopWatchStorage()


@router.on_command(StopWatchInterface.create_stopWatch)
@router.on_button_callback(StopWatchInterface.create_stopWatch)
async def create_stopWatch(ctx: aiomax.CommandContext, cursor: fsm.FSMCursor):
    if ctx.user_id in stopWatchStorage.stopWatchStorage:
        sw = stopWatchStorage.get(ctx.user_id)
        await router.bot.delete_message(str(sw.msg_start))
    stopWatch = StopWatch(ctx.user_id, time.time())
    if cursor.get_data() is not None and "task" in cursor.get_data():
        stopWatch.addTask(cursor.get_data()["task"])
        cursor.clear()
        kb = aiomax.buttons.KeyboardBuilder()
        kb.add(aiomax.buttons.CallbackButton("Запустить секундомер", StopWatchInterface.start_stopWatch))
        m = await ctx.message.reply(
            f"Секундомер создан. Вы можете запустить его",
            keyboard=kb
        )
    else:
        kb = aiomax.buttons.KeyboardBuilder()
        btn1 = aiomax.buttons.CallbackButton("Запустить секундомер", StopWatchInterface.start_stopWatch)
        btn2 = aiomax.buttons.CallbackButton("Выбрать задачу", TaskInterface.choose_task)
        kb.row(btn1, btn2)

        m = await ctx.message.reply(
            f"Секундомер создан. Вы можете запустить его или выбрать задачу.",
            keyboard=kb
        )
    stopWatch.addMsgId(m.id)
    stopWatchStorage.add(stopWatch)


@router.on_command(StopWatchInterface.start_stopWatch)
@router.on_button_callback(StopWatchInterface.start_stopWatch)
async def start_stopWatch(ctx: aiomax.CommandContext):
    kb = aiomax.buttons.KeyboardBuilder()
    btn = aiomax.buttons.CallbackButton("Остановить секундомер", StopWatchInterface.stop_stopWatch)
    kb.add(btn)

    timer = stopWatchStorage.get(ctx.user_id)
    timer.setTimeStart(time.time())

    await ctx.message.reply(
        f"Секундомер запущен в {time.strftime('%H:%M')}",
        keyboard=kb
    )


@router.on_button_callback("stop_stopWatch")
async def end_timer(ctx: aiomax.CommandContext):
    timer = stopWatchStorage.get(ctx.user_id)
    timer.time_end = time.time()
    kb = aiomax.buttons.KeyboardBuilder()
    btn1 = aiomax.buttons.CallbackButton("Главное меню", "start")
    kb.add(btn1)
    t = time.localtime(time.time() - timer.time_start)
    if timer.task:
        timer.task.addTime(t)
    await ctx.reply(
        f"Время работы: {time.strftime('%M:%S', t)}\nСекундомер остановился в {time.strftime('%H:%M')}",
        keyboard=kb
    )
