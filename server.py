'''
Переписать сервис из домашнего задания по Flask на aiohttp.
Результатом работы является API, написанный на aiohttp.

pip install aiohttp
pip install aiohttp[speedups]
pip install asyncpg
pip install sqlalchemy[asyncio] - именно так, иначе ошибка No module named 'greenlet'
pip install bcrypt           - для хеширования пароля

docker-compose up

'''

from aiohttp import web
from models import Adverts, Session, engine
import json
from typing import Type
from sqlalchemy.exc import IntegrityError 
from aiohttp.typedefs import Handler
import bcrypt

app = web.Application()                  

'''
Функция контекстная позволяет выполнить действия на старте работы приложения и после его 
завершения. Принимают экземпляр класса aiohttp (нашего приложения), код разделяется
yield. Все, что выше, выполняется при старте приложения. Все, что ниже - после завершения
работы приложения. 
'''
async def orm_context(app: web.Application):
    print('START')
    async with engine.begin() as conn:                  #вырываем из engin 1 подключение
        await conn.run_sync(Adverts.metadata.create_all)   #проводим миграцию
    yield
    await engine.dispose()                          #закрываем соединение с базой
    print('FINISH')

'''
Функция миддлеваре позволяет запускать сессию перед каждым запросом.
Принимает реквест и хэндлер. Хендлер - это программа, выполняющая запросы get, patch ..
'''
@web.middleware
async def session_middleware(request: web.Request, handler: Handler):
    async with Session() as session:         # перед началом запроса создаем сессию
        request.session = session           # прикрепляем ее к объекту реквест
        response = await handler(request)   # отправляем запрос
        return response                     # возвращаем респонз



app.cleanup_ctx.append(orm_context)                 #регистрируем контекстную функцию
app.middlewares.append(session_middleware)          #регистрируем мидлваре


def get_http_error(error_class: Type[web.HTTPClientError], message):
    return error_class(
        text=json.dumps({'error': message}), content_type='application/json'
    )


# async def get_adv_by_id(session: Session, adv_id: int) -> Adverts:
#     adv = await session.get(Adverts, adv_id)
#     if adv is None:
#         raise get_http_error(web.HTTPNotFound, f'Advertisement with id {adv_id} not found')
#     return adv
#
async def get_adv_by_id(adv_id: int, session: Session):
    advert = await session.get(Adverts, adv_id)
    if advert is None:
        raise web.HTTPNotFound(text=json.dumps({'status': 'error', 'message': 'advert not found'}),
                            content_type='application/json')
    return advert
#


    
async def add_adv(session: Session, adv: Adverts):
    try:
        session.add(adv)
        await session.commit()
    except IntegrityError as error:
        raise get_http_error(web.HTTPConflict, 'Advertisement already exists')
    return adv

class AdvertsView(web.View):

    @property                                  
    def avd_id(self):                          
        return int(self.request.match_info['adv_id'])
    
    @property
    def session(self) -> Session:              
        return self.request.session

    # async def get(self):
    #     adv = await get_adv_by_id(self.session, self.adv_id) 
    #     return web.json_response(adv.dict) 

    async def get(self):
        adv = await get_adv_by_id(int(self.request.match_info['adv_id']), 
                                  self.request.session)
        return web.json_response(adv.dict) 

    async def post(self):
        adv_data = await self.request.json()
        adv = Adverts(**adv_data)
        adv = await add_adv(self.session, adv)
        return web.json_response({'id': adv.id})   

    async def patch(self):
        # adv = await get_adv_by_id(self.session, self.adv_id) 
        # adv_data = await self.request.json()  
        # for field, value in adv_data.items():
        #     setattr(adv, field, value)   
        #     await add_adv(self.session, adv)
        # return web.json_response({'id': adv.id})   

        adv = await get_adv_by_id(int(self.request.match_info['adv_id']), 
                                  self.request.session)
        adv_data = await self.request.json()  
        for field, value in adv_data.items():
            setattr(adv, field, value)   
            await add_adv(self.session, adv)
        return web.json_response({'id': adv.id})   



    async def delete(self):
        # adv = await get_adv_by_id(self.session, self.adv_id) 
        adv = await get_adv_by_id(int(self.request.match_info['adv_id']), 
                                  self.request.session)
        await self.session.delete(adv)
        await self.session.commit()        
        return web.json_response({'status': 'ok'})




app.add_routes([                            
    web.get('/adv/{adv_id:\d+}', AdvertsView),
    web.patch('/adv/{adv_id:\d+}', AdvertsView),
    web.delete('/adv/{adv_id:\d+}', AdvertsView),
    web.post('/adv/', AdvertsView),
])



web.run_app(app)                        # запускаем    
