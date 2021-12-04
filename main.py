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
global_data_config = {
  "recent_action_count": {
    "url": "https://getquicker.net/Share",
    "regex": r'title="今日更新动作">(\d+)</span>',
  },
}
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
    return Response(content=svg, media_type="text/css", headers={'cache-control': 'public, max-age=20'})

# test url: http://127.0.0.1:8000/likes?id=2a98fd68-6628-4ca5-8edb-08d639a457d1
@app.get("/likes")
async def likes_action(id: str):
  
    html = await session.get(f'https://getquicker.net/Share/VoteActionUsers?actionId={id}')
    likes = int(re.search(r'共\s*<span>(\d+)</span>\s*人', html.text).group(1))
    
    # create response
    css = f'''.action-likes::before, .action-likes::before {{
      content: "{likes}";
    }}'''
    return Response(content=css, media_type="text/css", headers={'cache-control': 'public, max-age=60'})

# test url: http://127.0.0.1:8000/likes/skin?id=ce9a55ca-9725-4e28-4f9c-08d9b15ebac3
@app.get("/likes/skin")
async def likes_skin(id: str):
  
    html = await session.get(f'https://getquicker.net/Skins/View?id={id}')
    likes = int(re.search(r'查看外观设置文档(\'|")>(\d+)</span>', html.text).group(1))
    
    # create response
    css = f'''.skin-likes::before {{
      content: "{likes}";
    }}'''
    return Response(content=css, media_type="text/css", headers={'cache-control': 'public, max-age=60'})
  
# test url: http://127.0.0.1:8000/data/recent_action_count
# test url: http://127.0.0.1:8000/data/action-likes?url=https%3a%2f%2fgetquicker.net%2fShare%2fVoteActionUsers%3factionId%3d2a98fd68-6628-4ca5-8edb-08d639a457d1&regex=%e5%85%b1%5cs*%3cspan%3e(%5cd%2b)%3c%2fspan%3e%5cs*%e4%ba%ba
@app.get("/data/{item}")
async def get_data(item: str, url: str = None, regex: str = None):
    config = global_data_config.get(item, {})
    url = config.get('url', url)
    regex = config.get('regex', regex)
    if url is None or regex is None:
        return {'error': 'url or regex is None'}
    html = await session.get(url)
    likes = int(re.search(regex, html.text).group(1))
    
    # create response
    css = f'''.{item.replace('_', '-')}::before {{
      content: "{likes}";
    }}'''
    return Response(content=css, media_type="text/css", headers={'cache-control': 'public, max-age=30'})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
