from proxy_plus import dist
import pytest
import asyncio


@pytest.fixture()
async def async_factory():
    def factory(result=None, fail=False):
        async def async_func(*args, **kwargs):
            await asyncio.sleep(0)
            if fail:
                raise result
            return result

        return async_func

    return factory


@pytest.mark.asyncio
class TestDist:
    async def test_round_robin(self, async_factory):
        f1 = async_factory(1)
        f2 = async_factory(2)
        cc = dist.RoundRobinCreateConnnection([f1, f2])
        assert f1 == cc.choose()
        assert f2 == cc.choose()
        assert await cc() == 1
        assert await cc() == 2

    async def test_random(self, async_factory):
        funcs = [async_factory(i) for i in range(10)]
        cc = dist.RandomCreateConnection(funcs)
        a = set()
        for i in range(100):
            a.add(await cc())
        assert not set(range(10)).difference(a)

    async def test_on_failure(self, async_factory):
        f1 = async_factory(RuntimeError(), fail=True)
        f2 = async_factory(2)
        cc = dist.PriorityCreateConnection([f1,f2])
        assert cc.choose() == f1
        assert await cc() == 2
        cc_fail = dist.PriorityCreateConnection([f1, f1])
        with pytest.raises(RuntimeError):
            await cc_fail()
