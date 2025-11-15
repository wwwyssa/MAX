import aiomax
from aiomax import fsm
import time
from interfaces import StopWatchInterface, TaskInterface


class Task:
    name: str
    value: int
    time: time.struct_time

    def __init__(self, name: str, value: int) -> None:
        self.name = name
        self.value = value
        self.time = time.localtime(0)

    def setName(self, name: str) -> None:
        self.name = name

    def setValue(self, value: int) -> None:
        self.value = value

    def addTime(self, t: time.struct_time) -> None:
        self.time = time.struct_time([self.time[i] + t[i] for i in range(len(self.time))])
        print(self.time)


class TaskStorage:
    taskStorage: dict[int: list[Task]]

    def __init__(self):
        self.taskStorage = {}

    def addTask(self, id: int, task: Task):
        if id in self.taskStorage:
            self.taskStorage[id].append(task)
        else:
            self.taskStorage[id] = [task]

    def updateTask(self, id: int, prev_name: str, new_name: str, new_value: int):
        for t in self.taskStorage[id]:
            if t.name == prev_name:
                t.setName(new_name)
                t.setValue(new_value)
                break

    def deleteTask(self, id: int, name: str):
        self.taskStorage[id] = [t for t in self.taskStorage[id] if t.name != name]

    def getTasks(self, id: int) -> list[Task]:
        if id not in self.taskStorage:
            self.taskStorage[id] = []
        return self.taskStorage[id]


taskStorage = TaskStorage()
router = aiomax.Router()


@router.on_command(TaskInterface.list_tasks)
@router.on_button_callback(TaskInterface.list_tasks)
async def list_tasks(ctx: aiomax.CommandContext):
    tasks = taskStorage.getTasks(ctx.user_id)
    text = ""
    if len(tasks) == 0:
        text = "Вы не создали ни одной задачи"
    else:
        tasks.sort(key=lambda x: x.time, reverse=True)
        for t in tasks[:10]:
            text += f"<b>{t.name}</b>({t.value}): {time.strftime('%M:%S', t.time)}\n"
    kb = aiomax.buttons.KeyboardBuilder()
    kb.row(aiomax.buttons.CallbackButton("Создать задачу", TaskInterface.create_task))
    kb.add(aiomax.buttons.CallbackButton("Изменить задачу", TaskInterface.update_task))
    kb.add(aiomax.buttons.CallbackButton("Удалить задачу", TaskInterface.delete_task))
    kb.row(aiomax.buttons.CallbackButton("Меню", "start"))
    await ctx.send(text, keyboard=kb, format="html")


@router.on_button_callback(TaskInterface.create_task)
@router.on_command(TaskInterface.create_task)
async def create_task(ctx: aiomax.CommandContext, cursor: fsm.FSMCursor):
    await ctx.send("Введите название задачи")
    cursor.change_state(TaskInterface.write_task_name)


@router.on_message(aiomax.filters.state(TaskInterface.write_task_name))
async def write_task_name(msg: aiomax.Message, cursor: fsm.FSMCursor):
    await msg.reply("Введите ценность задачи (1 - 10)")
    cursor.change_state(TaskInterface.write_task_value)
    if cursor.get_data() is None or "name" not in cursor.get_data():
        cursor.change_data({"name": msg.content})


@router.on_message(aiomax.filters.state(TaskInterface.write_task_value))
async def write_task_value(msg: aiomax.Message, cursor: fsm.FSMCursor):
    try:
        print(f"************{int(msg.content)}")
        v = int(msg.content)
        if v < 1 or v > 10:
            print(v)
            raise Exception
        name = cursor.get_data()["name"]
        task = Task(name, v)
        taskStorage.addTask(msg.user_id, task)
        cursor.clear()
        kb = aiomax.buttons.KeyboardBuilder()
        kb.add(aiomax.buttons.CallbackButton("Вернуться к списку задач", TaskInterface.list_tasks))
        await msg.send("Задача добавлена", keyboard=kb)
    except Exception as e:
        await msg.send(f"Неверно введена ценность задачи: {e}")
        cursor.change_state(TaskInterface.write_task_name)


@router.on_button_callback(TaskInterface.update_task)
@router.on_command(TaskInterface.update_task)
async def update_task(ctx: aiomax.CommandContext, cursor: fsm.FSMCursor):
    await ctx.send("Введите название задачи которую хотите изменить")
    cursor.change_state(TaskInterface.update_task_choose)


@router.on_message(aiomax.filters.state(TaskInterface.update_task_choose))
async def update_task_choose(msg: aiomax.Message, cursor: fsm.FSMCursor):
    task_names = [t.name for t in taskStorage.getTasks(msg.user_id)]
    if msg.content in task_names:
        await msg.send("Введите новое название задачи")
        cursor.change_data({"prev_name": msg.content})
        cursor.change_state(TaskInterface.update_task_name)
    else:
        kb = aiomax.buttons.KeyboardBuilder()
        kb.add(aiomax.buttons.CallbackButton("Вернуться к списку задач", TaskInterface.list_tasks))
        cursor.clear()
        await msg.send("Такой задачи не существует", keyboard=kb)


@router.on_message(aiomax.filters.state(TaskInterface.update_task_name))
async def update_task_name(msg: aiomax.Message, cursor: fsm.FSMCursor):
    await msg.reply("Введите ценность задачи (1 - 10)")
    cursor.change_state(TaskInterface.write_task_value)
    if "name" not in cursor.get_data():
        cursor.change_data({"name": msg.content})


@router.on_message(aiomax.filters.state(TaskInterface.update_task_value))
async def update_task_value(msg: aiomax.Message, cursor: fsm.FSMCursor):
    try:
        v = int(msg.content)
        if v < 1 or v > 10:
            raise Exception
        prev_name = cursor.get_data()["prev_date"]
        name = cursor.get_data()["name"]
        taskStorage.updateTask(msg.user_id, prev_name, name, v)
        cursor.clear()
        kb = aiomax.buttons.KeyboardBuilder()
        kb.add(aiomax.buttons.CallbackButton("Вернуться к списку задач", TaskInterface.list_tasks))
        await msg.send("Задача обновлена", keyboard=kb)

    except Exception:
        await msg.send("Неверно введена ценность задачи")
        cursor.change_state(TaskInterface.update_task_name)


@router.on_button_callback(TaskInterface.delete_task)
@router.on_command(TaskInterface.delete_task)
async def delete_task(ctx: aiomax.CommandContext, cursor: fsm.FSMCursor):
    await ctx.send("Введите название задачи")
    cursor.change_state(TaskInterface.delete_task_choose)


@router.on_message(aiomax.filters.state(TaskInterface.delete_task_choose))
async def delete_task_choose(msg: aiomax.Message, cursor: fsm.FSMCursor):
    task_names = [t.name for t in taskStorage.getTasks(msg.user_id)]
    if msg.content in task_names:
        taskStorage.deleteTask(msg.user_id, msg.content)
        kb = aiomax.buttons.KeyboardBuilder()
        kb.add(aiomax.buttons.CallbackButton("Вернуться к списку задач", TaskInterface.list_tasks))
        cursor.clear()
        await msg.send("Задача удалена", keyboard=kb)
    else:
        kb = aiomax.buttons.KeyboardBuilder()
        kb.add(aiomax.buttons.CallbackButton("Вернуться к списку задач", TaskInterface.list_tasks))
        cursor.clear()
        await msg.send("Такой задачи не существует", keyboard=kb)


@router.on_button_callback(TaskInterface.choose_task)
@router.on_message(aiomax.filters.state(TaskInterface.choose_task))
async def choose_task(ctx: aiomax.CommandContext, cursor: fsm.FSMCursor):
    task_names = [t.name for t in taskStorage.getTasks(ctx.user_id)]
    if len(task_names) == 0:
        await ctx.send("Нет ни одной задачи")
    else:
        text = "Введи id задачи из списка\n"
        for i in range(len(task_names)):
            text += f"{i + 1} - {task_names[i]}\n"
        await ctx.send(text)
        cursor.change_state(TaskInterface.write_task_id)


@router.on_message(aiomax.filters.state(TaskInterface.write_task_id))
async def write_task_id(msg: aiomax.Message, cursor: fsm.FSMCursor):
    try:
        id = int(msg.content)
        if id < 1 or id > len(taskStorage.getTasks(msg.user_id)):
            raise Exception
        cursor.clear_state()
        cursor.change_data({"task": taskStorage.getTasks(msg.user_id)[id - 1]})
        kb = aiomax.buttons.KeyboardBuilder()
        kb.add(aiomax.buttons.CallbackButton("Вернуться к секундомеру", StopWatchInterface.create_stopWatch))
        await msg.send("Задача выбрана", keyboard=kb)

    except Exception:
        await msg.send("Неверно введена ценность задачи")
        cursor.change_state(TaskInterface.choose_task)
