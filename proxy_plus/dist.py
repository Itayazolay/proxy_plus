import typing
import abc
import random


class DistributedCreateConnection:
    __metaclass__ = abc.ABCMeta

    def __init__(self, create_connection: typing.List[typing.Callable]):
        self._cb = create_connection

    async def __call__(self, *args, **kwargs):
        create_connection = self.choose()
        return await create_connection(*args, **kwargs)

    @abc.abstractmethod
    def choose(self) -> typing.Callable: pass

    def add(self, create_connection: typing.Callable):
        self._cb.append(create_connection)


class RoundRobinCreateConnnection(DistributedCreateConnection):
    def choose(self) -> typing.Callable:
        cb = self._cb.pop(0)
        self._cb.append(cb)
        return cb


class RandomCreateConnection(DistributedCreateConnection):
    def choose(self) -> typing.Callable:
        return random.choice(self._cb)


class PriorityCreateConnection(RoundRobinCreateConnnection):
    async def __call__(self, *args, **kwargs):
        first = cc = self.choose()
        err = None
        while first != cc or err is None:
            try:
                return await cc(*args, **kwargs)
            except Exception as e:
                err = e
                cc = self.choose()
        raise err
