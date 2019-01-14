import typing
import abc
import random


class DistributedCreateConnection:
    """
    Base class for distributed create connection.
    This is used in order to use create connection from different client every time.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, create_connection: typing.List[typing.Callable]):
        """
        :param create_connection: List of create connection coroutines.
        """
        self._cb = create_connection

    async def __call__(self, *args, **kwargs):
        """Call the chosen create connection"""
        create_connection = self.choose()
        return await create_connection(*args, **kwargs)

    @abc.abstractmethod
    def choose(self) -> typing.Callable: pass

    def add(self, create_connection: typing.Callable):
        """
        Add new create connection couroutine.
        :param create_connection: Create connection coro to add.
        """
        self._cb.append(create_connection)


class RoundRobinCreateConnnection(DistributedCreateConnection):
    """Round robin implementation for Dist create connection."""
    def choose(self) -> typing.Callable:
        cb = self._cb.pop(0)
        self._cb.append(cb)
        return cb


class RandomCreateConnection(DistributedCreateConnection):
    """Choose the create connection randomly."""
    def choose(self) -> typing.Callable:
        return random.choice(self._cb)


class PriorityCreateConnection(RoundRobinCreateConnnection):
    """Choose create connection coro by priority. If one fails try the nextl."""
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
