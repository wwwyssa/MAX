class Task:
    name: str
    value: int

    def __init__(self, name: str, value: int) -> None:
        self.name = name
        self.value = value


class Timer:
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

    def set_time_start(self, time_start: float) -> None:
        self.time_start = time_start

    def add_msg_id(self, msg_id) -> None:
        self.msg_start = msg_id

    def add_task(self, task: Task) -> None:
        self.task = task


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


class User:
    id: int
    name: str
    points: int
    tasks: list[Task]
    time_spent: float

    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name
        self.points = 0
        self.tasks = []
        self.time_spent = 0.0

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def add_points(self, points: int) -> None:
        self.points += points

    def add_time_spent(self, time_spent: float) -> None:
        self.time_spent += time_spent

    def get_tasks(self) -> list[Task]:
        return self.tasks

    def get_points(self) -> int:
        return self.points

    def get_time_spent(self) -> float:
        return self.time_spent


class MapUser:
    users: dict[int: User]

    def __init__(self):
        self.users = {}

    def add(self, user: User) -> None:
        self.users[user.id] = user

    def get(self, id: int) -> User:
        return self.users[id]

    def delete(self, id: int) -> None:
        del self.users[id]
