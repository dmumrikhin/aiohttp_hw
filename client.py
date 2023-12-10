import asyncio
import aiohttp

async def main():

    async with aiohttp.ClientSession() as session:  # создаем сессию
        # async with session.post('http://127.0.0.1:8080/adv/',
        #                         json={
        #                             'header': 'header_1',
        #                             'description': 'description_1',
        #                             'owner': 'owner_1'
        #                         }, 
        #                         ) as response:
        #     print(response.status)
        #     print(await response.text())

        # async with session.patch('http://127.0.0.1:8080/adv/1',
        #                          json={'header': 'new_header'}
        #                         ) as response:
        #     print(response.status)
        #     print(await response.text())
            
        # async with session.delete('http://127.0.0.1:8080/adv/1',
        #                         ) as response:
        #     print(response.status)
        #     print(await response.text())

        async with session.get('http://127.0.0.1:8080/adv/5',
                                ) as response:
            print(response.status)
            print(await response.text())

asyncio.run(main())

