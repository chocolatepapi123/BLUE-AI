import unittest, math
from engine.core import load_csv, analyze, backtest, generate_signal, extract_concepts, optimize
class EngineTests(unittest.TestCase):
 def makebars(self,n=180):
  bars=[]; p=1.1000
  for i in range(n):
   # Deterministic repeating volatility/drift
   o=p; c=o+(0.0002 if i%9<5 else -0.00017); h=max(o,c)+0.0001; l=min(o,c)-0.0001
   bars.append({'time':f'{i}','open':o,'high':h,'low':l,'close':c,'volume':1}); p=c
  return bars
 def test_csv_parser(self):
  csv='timestamp,open,high,low,close,volume\n'+''.join(f'{i},1,1.2,0.8,1.1,3\n' for i in range(12))
  bars=load_csv(csv); self.assertEqual(len(bars),12); self.assertEqual(bars[0]['time'],'0')
 def test_analyzer_schema(self):
  a=analyze(self.makebars()); self.assertIn(a['bias'],['bullish','bearish','neutral']); self.assertIn('fvg',a)
 def test_backtest_metrics(self):
  b=backtest(self.makebars()); self.assertIn('expectancyR',b); self.assertEqual(b['count'],len(b['trades']))
 def test_signal_is_structured(self):
  s=generate_signal(self.makebars()); self.assertIn('reason',s)
 def test_concepts(self):
  c=extract_concepts('Buy side liquidity sweep, displacement, FVG, MSS and order block.')
  self.assertIn('sweep',c); self.assertIn('fair_value_gap',c); self.assertIn('market_structure',c)
 def test_optimizer_requires_data(self):
  with self.assertRaises(ValueError): optimize(self.makebars(40))
 def test_extract_research_profile(self):
  from engine.core import extract_research_profile
  p=extract_research_profile('Trade EURUSD and XAUUSD on M5 and H1 during London and New York. Look for liquidity sweep, FVG, displacement and MSS.')
  self.assertIn('EURUSD',p['symbols']); self.assertIn('XAUUSD',p['symbols'])
  self.assertIn('M5',p['timeframes']); self.assertIn('H1',p['timeframes'])
  self.assertIn('London',p['sessions']); self.assertIn('New York',p['sessions']); self.assertIn('fvg',p['setupTerms'])

if __name__=='__main__':unittest.main()
