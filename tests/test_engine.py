import sys, unittest
sys.path.insert(0,'.')
from engine.core import load_csv, analyze, backtest
class EngineTests(unittest.TestCase):
 def test_csv_and_analysis(self):
  csv='time,open,high,low,close\n'+'\n'.join(f'{i},{1+i*.001},{1.002+i*.001},{.999+i*.001},{1.001+i*.001}' for i in range(30))
  bars=load_csv(csv); self.assertEqual(len(bars),30); self.assertIn('bias',analyze(bars))
 def test_bad_headers(self):
  with self.assertRaises(ValueError): load_csv('x,y\n1,2')
 def test_backtest_schema(self):
  bars=[{'time':str(i),'open':100,'high':101,'low':99,'close':100} for i in range(40)]
  result=backtest(bars); self.assertEqual(result['count'],0); self.assertIn('expectancyR',result)
if __name__=='__main__': unittest.main()
