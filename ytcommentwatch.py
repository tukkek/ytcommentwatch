#!/usr/bin/python3
import sys,isodate,time,threading,os,random,urllib,tempfile
from googleapiclient.discovery import build
from oauth2client import file, client, tools
from httplib2 import Http

if len(sys.argv)<2:
  print(f'Usage: {sys.argv[0]} videoId')
  sys.exit(1)
  
DEBUG=False
WORDSPERSECOND=200/60
SECONDSPERWORD=1/WORDSPERSECOND

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
  part='snippet,replies',videoId=videoid,textFormat='plainText',maxResults=50,order='relevance')):
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
  current=[]
  while len(threads)>0 or len(current)>0:
    if len(current)==0:
      #earlier comments are more relevant
      #choose randomly but prefer early ones
      a=random.randrange(len(threads))
      b=random.randrange(len(threads))
      current=threads.pop(a if a<b else b)
    t=current.pop(0)
    comment=t['snippet']['textDisplay']
    readingtime=len(comment.split(' '))*SECONDSPERWORD
    path=False
    with tempfile.NamedTemporaryFile(delete=False,mode='w') as tmp:
      if DEBUG:
        print(f'Duration: {round(duration/60)}m ({round(duration/60**2)}h).',file=tmp)
        print(f'Total coments: {comments}.',file=tmp)
        print(f'Delay: {round(delay)}s ({round(delay/60)}m).',file=tmp)
        print()
      print(comment,file=tmp)
      path=tmp.name
    os.system('clear')
    os.system(f'fold -s -w `tput cols` {path}')
    time.sleep(readingtime if readingtime>delay else delay)
    
service=get_authenticated_service()
videosservice=service.videos()
comments=service.commentThreads()
threads=[]
videoid=sys.argv[1]
video=False

if 'youtube.com' in videoid:
  videoid=urllib.parse.urlparse(videoid).query
  videoid=urllib.parse.parse_qs(videoid)['v'][0]
elif 'youtu.be' in videoid:
  videoid=urllib.parse.urlparse(videoid).path.replace('/','')

for v in pages(videosservice,videosservice.list(part='contentDetails,statistics',id=videoid,maxResults=1)):
  video=v
  break
f=threading.Thread(target=fetch,args=[threads])
d=threading.Thread(target=display,args=[threads])
f.start()
d.start()
f.join()
d.join()
