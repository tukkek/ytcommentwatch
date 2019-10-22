#!/usr/bin/python3
import sys,isodate,time,threading,os,random
from googleapiclient.discovery import build
from oauth2client import file, client, tools
from httplib2 import Http

DEBUG=False
MINDELAY=9

if len(sys.argv)<2:
  print(f'Usage: {sys.argv[0]} videoid')
  sys.exit(1)

def get_authenticated_service():
  store=file.Storage('credentials.json')
  creds=store.get()
  if not creds or creds.invalid:
      flow=client.flow_from_clientsecrets('client_secret.json', ['https://www.googleapis.com/auth/youtube.force-ssl'])
      creds=tools.run_flow(flow,store,tools.argparser.parse_args(args=[]))
  return build('youtube','v3',http=creds.authorize(Http()))
def pages(service,request,follow=True): #TODO return items
  i=0
  while request:
    try:
      response=request.execute()
    except Exception as e:
      print(e)
      continue
    for item in response['items']:
      yield item
    if not follow:
      return
    request=service.list_next(request,response)
def fetch(threads):
  for thread in pages(comments,comments.list(
  part='snippet,replies',videoId=sys.argv[1],textFormat='plainText',maxResults=50,order='relevance')):
    t=[]
    t.append(thread['snippet']['topLevelComment'])
    if 'replies' in thread:
      for r in thread['replies']['comments']:
        t.append(r)
    threads.append(t)
def display(threads):
  while(len(threads)==0):
    os.system('clear')
    time.sleep(1)
  duration=isodate.parse_duration(video['contentDetails']['duration']).total_seconds()
  comments=int(video['statistics']['commentCount'])
  delay=duration/comments
  if delay<MINDELAY:
    delay=MINDELAY
  current=[]
  while len(threads)>0 or len(current)>0:
    if len(current)==0:
      current=threads.pop(random.randrange(len(threads)))
    t=current.pop(0)
    os.system('clear')
    if DEBUG:
      print(f'Duration: {round(duration/60)}m ({round(duration/60**2)}h).')
      print(f'Total coments: {comments}.')
      print(f'Delay: {round(delay)}s ({round(delay/60)}m).')
      print()
    print(t['snippet']['textDisplay'])
    time.sleep(delay)
    
service=get_authenticated_service()
videosservice=service.videos()
comments=service.commentThreads()
threads=[]

video=False
for v in pages(videosservice,videosservice.list(part='contentDetails,statistics',id=sys.argv[1],maxResults=1)):
  video=v
  break
f=threading.Thread(target=fetch,args=[threads])
d=threading.Thread(target=display,args=[threads])
f.start()
d.start()
f.join()
d.join()
