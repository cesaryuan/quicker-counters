from datetime import datetime
from fastapi import FastAPI
# from deta import Base
from starlette.responses import Response
import re
import httpx
from sqlitedict import SqliteDict

app = FastAPI()
# counters = Base("counters")
counters = SqliteDict('./data/my_db.sqlite', autocommit=True)

session = httpx.AsyncClient()

@app.get("/")
async def root():    
    return "Hello World!"

# test url: http://127.0.0.1:8000/hits?id=111
@app.get("/hits", )
async def hits(id: str, font='DejaVu Sans, Verdana, Geneva, sans-serif'):
    # 获取counter并更新数据库
    # counter = counters.get(id)
    counter = counters.get(id, {
            'key': id,
            'allCount': 0,
            'todayCount': 0,
            'lastUpdateTime': datetime.now().day
          })
    if counter is None:
        counter = {
            'key': id,
            'allCount': 0,
            'todayCount': 0,
            'lastUpdateTime': datetime.now().day
          }
        counters[id] = counter
    counter['allCount'] += 1
    if counter['lastUpdateTime'] != datetime.now().day:
        counter['todayCount'] = 0
        counter['lastUpdateTime'] = datetime.now().day
    else:
        counter['todayCount'] += 1
    counters[id] = counter
    
    count = counter['allCount']
    todayCount = counter['todayCount']
    
    # create response
    svg = f'''.total-hit-times::before, .hit-times::before {{
      content: "{count}";
    }}
    .today-hit-times::before {{
      content: "{todayCount}";
    }}'''
    return Response(content=svg, media_type="text/css", headers={'cache-control': 'private, max-age=20'})

# test url: http://127.0.0.1:8000/likes?id=2a98fd68-6628-4ca5-8edb-08d639a457d1
@app.get("/likes")
async def hits(id: str):
  
    html = await session.get(f'https://getquicker.net/Share/VoteActionUsers?actionId={id}')
    likes = int(re.search(r'共\s*<span>(\d+)</span>\s*人', html.text).group(1))
    
    # create response
    css = f'''.action-likes::before, .action-likes::before {{
      content: "{likes}";
    }}'''
    return Response(content=css, media_type="text/css", headers={'cache-control': 'private, max-age=60'})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
