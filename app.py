import asyncio


async def launch():
    from src.athena.core.deus.athena.athena_instance import Athena

    athena = Athena()
    await athena.start()
    # For testing purposes:
    await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(launch())
