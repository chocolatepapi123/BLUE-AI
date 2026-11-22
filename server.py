from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, urllib.parse, os, threading, time, urllib.request, urllib.error
from engine.core import load_csv, analyze, backtest, researcher, multi_timeframe, generate_signal, optimize
ROOT=Path(__file__).parent; WEB=ROOT/'web'; DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)
def readjson(name,default):
 try:return json.loads((DATA/name).read_text())
 except:return default
def savejson(name,obj): (DATA/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,default=str))
def request_json(url,headers=None,timeout=15):
 req=urllib.request.Request(url,headers=headers or {'User-Agent':'Mozilla/5.0 BLUE-AI research client'})
 with urllib.request.urlopen(req,timeout=timeout) as r:return json.loads(r.read())
def yahoo_symbol(s):
 return {'EURUSD':'EURUSD=X','GBPUSD':'GBPUSD=X','USDJPY':'USDJPY=X','XAUUSD':'GC=F','XAGUSD':'SI=F','NAS100':'NQ=F','US30':'YM=F','SPX500':'ES=F'}.get(s.upper(),s)
def fetch_yahoo(symbol,interval='1h',range_='1mo'):
 label=interval.upper(); interval={'M1':'1m','M5':'5m','M15':'15m','M30':'30m','H1':'60m','H4':'60m','D1':'1d'}.get(label,interval); aggregate_h4=(label=='H4')
 sym=urllib.parse.quote(yahoo_symbol(symbol),safe=''); url=f'https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range={range_}&interval={interval}&includePrePost=false'
 data=request_json(url); result=data['chart']['result'][0]; q=result['indicators']['quote'][0]; bars=[]
 for i,t in enumerate(result['timestamp']):
  try:
   o,h,l,c=q['open'][i],q['high'][i],q['low'][i],q['close'][i]
   if None in (o,h,l,c):continue
   bars.append({'time':time.strftime('%Y-%m-%d %H:%M:%S UTC',time.gmtime(t)),'open':float(o),'high':float(h),'low':float(l),'close':float(c),'volume':float((q.get('volume') or [0]*len(result['timestamp']))[i] or 0)})
  except (IndexError,TypeError):continue
 if aggregate_h4:
  grouped=[]
  for i in range(0,len(bars)-3,4):
   chunk=bars[i:i+4]
   if len(chunk)<4:continue
   grouped.append({'time':chunk[0]['time'],'open':chunk[0]['open'],'high':max(x['high'] for x in chunk),'low':min(x['low'] for x in chunk),'close':chunk[-1]['close'],'volume':sum(x['volume'] for x in chunk)})
  bars=grouped
 if len(bars)<10:raise ValueError('Provider returned fewer than 10 candles')
 return bars
class Handler(SimpleHTTPRequestHandler):
  def __init__(self,*a,**kw):super().__init__(*a,directory=str(WEB),**kw)
  def send_json(self,obj,status=200):
   b=json.dumps(obj,allow_nan=False,default=str).encode(); self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(b))); self.send_header('Access-Control-Allow-Origin','*'); self.end_headers(); self.wfile.write(b)
  def body(self):
   n=int(self.headers.get('Content-Length','0')); return json.loads(self.rfile.read(n) or b'{}')
  def do_OPTIONS(self):self.send_response(204); self.send_header('Access-Control-Allow-Origin','*'); self.send_header('Access-Control-Allow-Headers','Content-Type'); self.send_header('Access-Control-Allow-Methods','GET,POST,DELETE,OPTIONS'); self.end_headers()
  def do_GET(self):
   path=urllib.parse.urlparse(self.path).path
   if path=='/api/state':return self.send_json({'knowledge':readjson('knowledge.json',[]),'strategies':readjson('strategies.json',[]),'markets':readjson('markets.json',{}),'settings':readjson('settings.json',{}),'signals':readjson('signals.json',[]),'scanLog':readjson('scanlog.json',[])[:100]})
   if path=='/api/health':return self.send_json({'ok':True,'app':'BLUE AI','version':'1.0-research','localAI':ollama_available()})
   if path=='/api/market-data':
    qs=urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
    try:return self.send_json({'bars':fetch_yahoo(qs.get('symbol',['EURUSD'])[0],qs.get('interval',['1h'])[0],qs.get('range',['1mo'])[0])})
    except Exception as e:return self.send_json({'error':str(e)},502)
   return super().do_GET()
  def do_POST(self):
   try:
    b=self.body(); route=urllib.parse.urlparse(self.path).path
    if route=='/api/youtube-transcript':
     url=b.get('url',''); match=__import__('re').search(r'(?:youtu\.be/|youtube\.com/(?:watch\?v=|shorts/|embed/))([A-Za-z0-9_-]{11})',url)
     if not match:return self.send_json({'error':'Could not recognize a YouTube video ID'},400)
     try:
      from youtube_transcript_api import YouTubeTranscriptApi
      transcript=YouTubeTranscriptApi().fetch(match.group(1)); content='\n'.join(x.text for x in transcript)
      return self.send_json({'ok':True,'videoId':match.group(1),'transcript':content})
     except ImportError:return self.send_json({'error':'Transcript library is not installed. Install dependencies in requirements.txt and restart.'},503)
     except Exception as ex:return self.send_json({'error':'Transcript unavailable or captions blocked: '+str(ex)},502)
    if route=='/api/knowledge':
     arr=readjson('knowledge.json',[]); item={'id':int(time.time()*1000),'title':b.get('title','Untitled'),'kind':b.get('kind','notes'),'url':b.get('url',''),'content':b.get('content',''),'concepts':[],'created':time.strftime('%Y-%m-%d %H:%M:%S')}; from engine.core import extract_concepts; item['concepts']=extract_concepts(item['content']); arr.insert(0,item); savejson('knowledge.json',arr); return self.send_json({'ok':True,'item':item})
    if route=='/api/delete-knowledge':
     arr=[x for x in readjson('knowledge.json',[]) if str(x['id'])!=str(b.get('id'))]; savejson('knowledge.json',arr); return self.send_json({'ok':True})
    if route=='/api/strategy':
     arr=readjson('strategies.json',[]); item=b; item['id']=item.get('id') or int(time.time()*1000); arr.insert(0,item); savejson('strategies.json',arr); return self.send_json({'ok':True,'strategies':arr})
    if route=='/api/delete-strategy':
     arr=[x for x in readjson('strategies.json',[]) if str(x.get('id'))!=str(b.get('id'))]; savejson('strategies.json',arr); return self.send_json({'ok':True})
    if route=='/api/upload-csv':
     bars=load_csv(b['csv']); markets=readjson('markets.json',{}); key=b.get('symbol','UNKNOWN').upper()+'_'+b.get('timeframe','M15').upper(); markets[key]={'symbol':b.get('symbol','UNKNOWN').upper(),'timeframe':b.get('timeframe','M15').upper(),'bars':bars,'source':'CSV','updated':time.strftime('%Y-%m-%d %H:%M:%S')}; savejson('markets.json',markets); return self.send_json({'ok':True,'key':key,'count':len(bars),'analysis':analyze(bars)})
    if route=='/api/fetch-market':
     symbol=b.get('symbol','EURUSD').upper(); tf=b.get('timeframe','1h'); bars=fetch_yahoo(symbol,tf,b.get('range','1mo')); markets=readjson('markets.json',{}); key=symbol+'_'+b.get('label',tf).upper(); markets[key]={'symbol':symbol,'timeframe':b.get('label',tf).upper(),'bars':bars,'source':'Yahoo Finance proxy data','updated':time.strftime('%Y-%m-%d %H:%M:%S')}; savejson('markets.json',markets); return self.send_json({'ok':True,'key':key,'count':len(bars),'analysis':analyze(bars)})
    if route in ('/api/analyze','/api/signal','/api/backtest','/api/optimize'):
     markets=readjson('markets.json',{}); key=b.get('key'); bars=markets.get(key,{}).get('bars')
     if not bars:return self.send_json({'error':'Dataset not found. Import candles or fetch data first.'},404)
     if route=='/api/optimize':return self.send_json(optimize(bars,float(b.get('risk_pct',1)),float(b.get('max_risk_pct',3))))
     if route=='/api/analyze':return self.send_json({'analysis':analyze(bars),'signal':generate_signal(bars,int(b.get('lookback',5)),float(b.get('bodyMultiple',1.25)),float(b.get('maxRiskPct',3)),float(b.get('rr',2))),'key':key,'market':markets[key]})
     if route=='/api/signal':
      sig=generate_signal(bars,int(b.get('lookback',5)),float(b.get('bodyMultiple',1.25)),float(b.get('maxRiskPct',3)),float(b.get('rr',2))); sig['key']=key; sig['symbol']=markets[key]['symbol']; sig['timeframe']=markets[key]['timeframe']; sig['checkedAt']=time.strftime('%Y-%m-%d %H:%M:%S'); logs=readjson('signals.json',[])
      if sig.get('signal'):
       sig['id']=int(time.time()*1000); logs.insert(0,sig); savejson('signals.json',logs[:500]); telegram_send(sig)
      return self.send_json(sig)
     params={k:b.get(k,default) for k,default in [('lookback',5),('rr',2.0),('risk_pct',1.0),('body_multiple',1.25),('max_risk_pct',3.0),('max_holding',80),('spread',0.0),('slippage',0.0)]}; params={k:(int(v) if k in ('lookback','max_holding') else float(v)) for k,v in params.items()}; result=backtest(bars,**params); result['key']=key; return self.send_json(result)
    if route=='/api/multi-timeframe':
     markets=readjson('markets.json',{}); sets={}
     selected=[markets[k] for k in b.get('keys',[]) if k in markets]
     if selected:
      symbol=selected[0].get('symbol')
      selected=[m for m in selected if m.get('symbol')==symbol]
     for market in selected:sets[market['timeframe']]=market['bars']
     return self.send_json(multi_timeframe(sets))
    if route=='/api/research':return self.send_json(researcher(readjson('knowledge.json',[]),readjson('strategies.json',[]),b.get('backtest')))
    if route=='/api/settings':
     s=readjson('settings.json',{}); s.update(b); savejson('settings.json',s); return self.send_json({'ok':True,'settings':s})
    if route=='/api/restore':
     for name,key in [('knowledge.json','knowledge'),('strategies.json','strategies'),('markets.json','markets'),('settings.json','settings'),('signals.json','signals'),('scanlog.json','scanLog')]:
      if key in b:savejson(name,b[key])
     return self.send_json({'ok':True})
    if route=='/api/reset':
     for name,default in [('knowledge.json',[]),('strategies.json',[]),('markets.json',{}),('settings.json',{}),('signals.json',[]),('scanlog.json',[])]:savejson(name,default)
     return self.send_json({'ok':True})
    if route=='/api/ollama':
     prompt=b.get('prompt',''); if_not= None
     if not prompt.strip():return self.send_json({'error':'Prompt is empty'},400)
     try:
      req=urllib.request.Request('http://127.0.0.1:11434/api/generate',data=json.dumps({'model':b.get('model','llama3.2'),'prompt':prompt,'stream':False}).encode(),headers={'Content-Type':'application/json'}); response=json.loads(urllib.request.urlopen(req,timeout=120).read()); return self.send_json({'response':response.get('response',''),'model':response.get('model')})
     except Exception as e:return self.send_json({'error':'Local Ollama unavailable: '+str(e)},503)
    if route=='/api/scan-now':return self.send_json(scan_once())
    return self.send_json({'error':'Unknown endpoint'},404)
   except Exception as e:return self.send_json({'error':str(e)},400)
def ollama_available():
 try:urllib.request.urlopen('http://127.0.0.1:11434/api/tags',timeout=1);return True
 except:return False
def telegram_send(signal):
 settings=readjson('settings.json',{}); token=settings.get('telegramToken'); chat=settings.get('telegramChatId')
 if not token or not chat:return False
 s=signal.get('signal')
 if not s:return False
 msg=f"BLUE AI setup alert\n{signal.get('symbol')} {signal.get('timeframe')} {s['direction']}\nEntry: {s['entry']}\nSL: {s['stop']}\nTP: {s['target']}\nRR: {s['rr']}\nRule: {s['rule']}\nResearch signal only — not financial advice."
 try:
  req=urllib.request.Request(f'https://api.telegram.org/bot{token}/sendMessage',data=urllib.parse.urlencode({'chat_id':chat,'text':msg}).encode()); urllib.request.urlopen(req,timeout=12);return True
 except:return False
def scan_once():
 settings=readjson('settings.json',{}); markets=readjson('markets.json',{}); results=[]; log=readjson('scanlog.json',[])
 if settings.get('autoRefreshMarkets'):
  for key,market in list(markets.items()):
   try:
    tf=market.get('timeframe','H1'); bars=fetch_yahoo(market.get('symbol','EURUSD'),tf,settings.get('fetchRange','1mo')); market['bars']=bars; market['source']='Yahoo Finance proxy data (scheduled refresh)'; market['updated']=time.strftime('%Y-%m-%d %H:%M:%S')
   except Exception as exc:market['refreshError']=str(exc)
  savejson('markets.json',markets)
 for key,market in markets.items():
  if key not in settings.get('watchlist',list(markets)):continue
  sig=generate_signal(market.get('bars',[]),int(settings.get('lookback',5)),float(settings.get('bodyMultiple',1.25)),float(settings.get('maxRiskPct',3)),float(settings.get('rr',2)))
  if sig.get('signal'):
   result={'key':key,'symbol':market['symbol'],'timeframe':market['timeframe'],'signal':sig['signal'],'reason':sig['reason'],'checkedAt':time.strftime('%Y-%m-%d %H:%M:%S')}; results.append(result)
   old=readjson('signals.json',[]); last=old[0] if old else {}; dedupe=f"{key}|{market.get('bars',[])[-1].get('time')}|{sig['signal']['direction']}"
   already=any(x.get('dedupe')==dedupe for x in old)
   if not already:result['id']=int(time.time()*1000); result['dedupe']=dedupe; old.insert(0,result);savejson('signals.json',old[:500]);telegram_send(result)
 log.insert(0,{'time':time.strftime('%Y-%m-%d %H:%M:%S'),'results':results}); savejson('scanlog.json',log[:100]); return {'checked':len(markets),'signals':results,'note':'Uses latest locally stored candle datasets; refresh market data before scanning.'}
def scheduler():
 while True:
  s=readjson('settings.json',{}); minutes=max(5,int(s.get('scanIntervalMinutes',30)))
  if s.get('autoScan'):scan_once()
  time.sleep(minutes*60)
if __name__=='__main__':
 threading.Thread(target=scheduler,daemon=True).start(); print('BLUE AI running at http://127.0.0.1:8765'); ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
