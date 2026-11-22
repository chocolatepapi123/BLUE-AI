from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, urllib.parse, os, traceback
from engine.core import load_csv, analyze, backtest, researcher
ROOT=Path(__file__).parent; WEB=ROOT/'web'; DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)

def readjson(name, default):
    p=DATA/name
    try:return json.loads(p.read_text())
    except:return default

def savejson(name, obj): (DATA/name).write_text(json.dumps(obj,indent=2))
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=str(WEB),**kw)
    def send_json(self,obj,status=200):
        b=json.dumps(obj,allow_nan=False).encode(); self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(b))); self.send_header('Access-Control-Allow-Origin','*'); self.end_headers(); self.wfile.write(b)
    def do_OPTIONS(self): self.send_response(204); self.send_header('Access-Control-Allow-Origin','*'); self.send_header('Access-Control-Allow-Headers','Content-Type'); self.send_header('Access-Control-Allow-Methods','GET,POST,OPTIONS'); self.end_headers()
    def do_GET(self):
        if self.path.startswith('/api/state'):
            return self.send_json({'knowledge':readjson('knowledge.json',[]),'strategies':readjson('strategies.json',[]),'markets':readjson('markets.json',{})})
        return super().do_GET()
    def do_POST(self):
        try:
            n=int(self.headers.get('Content-Length','0')); body=json.loads(self.rfile.read(n) or b'{}'); route=urllib.parse.urlparse(self.path).path
            if route=='/api/knowledge':
                arr=readjson('knowledge.json',[]); item={'id':len(arr)+1,'title':body.get('title','Untitled'),'kind':body.get('kind','notes'),'url':body.get('url',''),'content':body.get('content',''),'created':body.get('created','')}; arr.append(item); savejson('knowledge.json',arr); return self.send_json({'ok':True,'item':item})
            if route=='/api/strategy':
                arr=readjson('strategies.json',[]); arr.append(body); savejson('strategies.json',arr); return self.send_json({'ok':True,'strategies':arr})
            if route=='/api/upload-csv':
                bars=load_csv(body['csv']); markets=readjson('markets.json',{}); key=body.get('symbol','UNKNOWN')+'_'+body.get('timeframe','M15'); markets[key]={'symbol':body.get('symbol','UNKNOWN'),'timeframe':body.get('timeframe','M15'),'bars':bars}; savejson('markets.json',markets); return self.send_json({'ok':True,'key':key,'count':len(bars),'analysis':analyze(bars)})
            if route=='/api/analyze':
                markets=readjson('markets.json',{}); key=body.get('key'); bars=markets.get(key,{}).get('bars');
                if not bars:return self.send_json({'error':'Market dataset not found'},404)
                return self.send_json({'analysis':analyze(bars),'backtest':backtest(bars, int(body.get('lookback',5)),float(body.get('rr',2)),float(body.get('risk',1))),'key':key})
            if route=='/api/research':
                return self.send_json(researcher(readjson('knowledge.json',[]),readjson('strategies.json',[]),body.get('backtest')))
            if route=='/api/delete-knowledge':
                arr=readjson('knowledge.json',[]); arr=[x for x in arr if x['id']!=body.get('id')]; savejson('knowledge.json',arr); return self.send_json({'ok':True})
            return self.send_json({'error':'Unknown route'},404)
        except Exception as e: return self.send_json({'error':str(e)},400)
if __name__=='__main__':
    print('BLUE AI local server running at http://127.0.0.1:8765')
    ThreadingHTTPServer(('0.0.0.0',8765),Handler).serve_forever()
