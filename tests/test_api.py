import json, tempfile, threading, unittest, urllib.request
from http.server import ThreadingHTTPServer
import server
class APITests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory(); server.DATA=__import__('pathlib').Path(cls.temp.name)
  cls.http=ThreadingHTTPServer(('127.0.0.1',0),server.Handler); cls.port=cls.http.server_address[1]
  cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start();cls.base=f'http://127.0.0.1:{cls.port}/api'
 @classmethod
 def tearDownClass(cls):cls.http.shutdown();cls.thread.join();cls.temp.cleanup()
 def post(self,path,payload):
  req=urllib.request.Request(self.base+path,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'});return json.loads(urllib.request.urlopen(req).read())
 def get(self,path):return json.loads(urllib.request.urlopen(self.base+path).read())
 def test_health_and_backup_reset_routes(self):
  self.assertTrue(self.get('/health')['ok']);self.assertTrue(self.post('/restore',{'knowledge':[],'strategies':[],'markets':{},'settings':{},'signals':[],'scanLog':[]})['ok']);self.assertTrue(self.post('/reset',{})['ok'])
 def test_csv_upload_analyze_backtest_and_scan(self):
  rows=['time,open,high,low,close,volume'];price=1.2
  for i in range(60):
   o=price;c=o+(0.0001 if i%10<6 else -0.00009);h=max(o,c)+0.00003;l=min(o,c)-0.00003;rows.append(f'{i},{o},{h},{l},{c},5');price=c
  result=self.post('/upload-csv',{'csv':'\n'.join(rows),'symbol':'TEST','timeframe':'M5'});key=result['key'];self.assertEqual(result['count'],60)
  self.assertIn('analysis',self.post('/analyze',{'key':key}));self.assertIn('trades',self.post('/backtest',{'key':key}));self.assertIn('reason',self.post('/signal',{'key':key}));self.assertTrue(self.post('/reset',{})['ok'])
if __name__=='__main__':unittest.main()
