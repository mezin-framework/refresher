from redis import Redis

r = Redis()
r.lpush('high_priority_refresh_queue', {"username": "", "password": "", "work_id": "2"})
sub = r.pubsub()
sub.subscribe('2')
for item in sub.listen():
    print item
    print item['data']
    
