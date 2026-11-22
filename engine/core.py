"""BLUE AI research engine: deterministic technical analysis and testable rule execution."""
from __future__ import annotations
import csv, io, math, statistics, re
ALIASES={'time':['time','timestamp','date','datetime','date_time'],'open':['open','o'],'high':['high','h'],'low':['low','l'],'close':['close','c'],'volume':['volume','vol','v']}
def load_csv(text):
    rows=[]; reader=csv.DictReader(io.StringIO(text)); headers=reader.fieldnames or []; mapping={}
    for key,names in ALIASES.items():
        for h in headers:
            if h.lower().strip() in names: mapping[key]=h; break
    missing=[k for k in ('open','high','low','close') if k not in mapping]
    if missing: raise ValueError('Missing required columns: '+', '.join(missing))
    for row in reader:
        try:
            b={k:float(row[mapping[k]]) for k in ('open','high','low','close')}
            b['time']=str(row.get(mapping.get('time',''),'') if mapping.get('time') else len(rows)); b['volume']=float(row.get(mapping['volume']) or 0) if mapping.get('volume') else 0
            if b['high']<b['low'] or b['high']<max(b['open'],b['close']) or b['low']>min(b['open'],b['close']): continue
            rows.append(b)
        except (ValueError,TypeError,KeyError): continue
    if len(rows)<10: raise ValueError(f'Need at least 10 valid candles, got {len(rows)}')
    return rows

def pivots(bars,left=2,right=2):
    hi=[]; lo=[]
    for i in range(left,len(bars)-right):
        if all(bars[i]['high']>bars[j]['high'] for j in range(i-left,i)) and all(bars[i]['high']>=bars[j]['high'] for j in range(i+1,i+right+1)): hi.append((i,bars[i]['high']))
        if all(bars[i]['low']<bars[j]['low'] for j in range(i-left,i)) and all(bars[i]['low']<=bars[j]['low'] for j in range(i+1,i+right+1)): lo.append((i,bars[i]['low']))
    return hi,lo

def analyze(bars):
    if len(bars)<5: raise ValueError('At least 5 candles required')
    highs,lows=pivots(bars); last=bars[-1]; n=min(20,len(bars)); prev=bars[-min(6,len(bars)):-1]
    ph=max(x['high'] for x in prev); pl=min(x['low'] for x in prev)
    sweep_hi=last['high']>ph and last['close']<ph; sweep_lo=last['low']<pl and last['close']>pl
    avgbody=statistics.mean(abs(x['close']-x['open']) for x in bars[-n:-1]) or 1e-12; body=abs(last['close']-last['open']); displacement=body>=avgbody*1.5
    fvg=None
    if len(bars)>=3:
        a,b,c=bars[-3:]
        if a['high']<c['low']: fvg={'type':'bullish','low':a['high'],'high':c['low'],'size':c['low']-a['high']}
        elif a['low']>c['high']: fvg={'type':'bearish','low':c['high'],'high':a['low'],'size':a['low']-c['high']}
    sh=highs[-1][1] if highs else max(x['high'] for x in bars[-10:]); sl=lows[-1][1] if lows else min(x['low'] for x in bars[-10:]); midpoint=(sh+sl)/2
    bias='bullish' if last['close']>midpoint else 'bearish' if last['close']<midpoint else 'neutral'
    signals=[]
    if sweep_lo and displacement and last['close']>last['open']: signals.append({'direction':'BUY','reason':'Recent low sweep with bullish displacement','score':70+(15 if fvg and fvg['type']=='bullish' else 0)})
    if sweep_hi and displacement and last['close']<last['open']: signals.append({'direction':'SELL','reason':'Recent high sweep with bearish displacement','score':70+(15 if fvg and fvg['type']=='bearish' else 0)})
    return {'price':last['close'],'time':last['time'],'bias':bias,'swingHigh':sh,'swingLow':sl,'rangeMid':midpoint,'sweepHigh':sweep_hi,'sweepLow':sweep_lo,'displacement':displacement,'avgBody':avgbody,'lastBody':body,'fvg':fvg,'signals':signals,'pivotHighs':highs[-12:],'pivotLows':lows[-12:]}

def generate_signal(bars, lookback=5, body_multiple=1.25, max_risk_pct=3.0, rr=2.0):
    if len(bars)<lookback+5: return {'signal':None,'reason':'Insufficient candles'}
    c=bars[-1]; prior=bars[-lookback-1:-1]; high=max(b['high'] for b in prior); low=min(b['low'] for b in prior); avg=statistics.mean(abs(b['close']-b['open']) for b in bars[-min(20,len(bars)):-1]) or 1e-12; body=abs(c['close']-c['open']); side=None
    if c['low']<low and c['close']>low and c['close']>c['open'] and body>=avg*body_multiple: side='BUY'
    elif c['high']>high and c['close']<high and c['close']<c['open'] and body>=avg*body_multiple: side='SELL'
    if not side:return {'signal':None,'reason':'No rule-defined sweep and displacement setup'}
    entry=c['close']; stop=c['low'] if side=='BUY' else c['high']; risk=abs(entry-stop)
    if risk<=0 or risk/entry*100>max_risk_pct:return {'signal':None,'reason':'Risk distance rejected by configured limit'}
    target=entry+risk*rr if side=='BUY' else entry-risk*rr
    return {'signal':{'direction':side,'time':c['time'],'entry':entry,'stop':stop,'target':target,'rr':rr,'riskDistance':risk,'riskPercentPrice':risk/entry*100,'rule':'Range sweep + displacement','score':75},'reason':'Rule conditions met; not a trade recommendation'}

def backtest(bars, lookback=5, rr=2.0, risk_pct=1.0, body_multiple=1.25, max_risk_pct=3.0, max_holding=80, spread=0.0, slippage=0.0):
    trades=[]; equity=100.0; peak=equity; maxdd=0.0; start=max(lookback+3,20)
    for i in range(start,len(bars)-1):
        cur=bars[i]; prior=bars[i-lookback-1:i-1]; hi=max(x['high'] for x in prior); lo=min(x['low'] for x in prior); avg=statistics.mean(abs(x['close']-x['open']) for x in bars[max(0,i-20):i]) or 1e-12; body=abs(cur['close']-cur['open']); side=None
        if cur['low']<lo and cur['close']>lo and cur['close']>cur['open'] and body>=avg*body_multiple: side='long'
        elif cur['high']>hi and cur['close']<hi and cur['close']<cur['open'] and body>=avg*body_multiple: side='short'
        if not side: continue
        entry=cur['close']+(spread/2+slippage if side=='long' else -(spread/2+slippage)); stop=cur['low'] if side=='long' else cur['high']; dist=abs(entry-stop)
        if dist<=0 or dist/entry*100>max_risk_pct: continue
        tp=entry+dist*rr if side=='long' else entry-dist*rr; outcome=None; exitp=None; exitidx=None
        for j in range(i+1,min(i+max_holding+1,len(bars))):
            b=bars[j]; stop_hit=b['low']<=stop if side=='long' else b['high']>=stop; tp_hit=b['high']>=tp if side=='long' else b['low']<=tp
            if stop_hit: outcome=-1; exitp=stop; exitidx=j; break # pessimistic stop-first if both
            if tp_hit: outcome=rr; exitp=tp; exitidx=j; break
        if outcome is None: continue
        trades.append({'side':side,'entryTime':cur['time'],'exitTime':bars[exitidx]['time'],'entry':entry,'stop':stop,'target':tp,'exit':exitp,'r':outcome,'barsHeld':exitidx-i})
        equity*=1+(risk_pct/100)*outcome; peak=max(peak,equity); maxdd=max(maxdd,(peak-equity)/peak*100)
    wins=[t for t in trades if t['r']>0]; losses=[t for t in trades if t['r']<0]
    totalr=sum(t['r'] for t in trades); grosswin=sum(t['r'] for t in wins); grossloss=abs(sum(t['r'] for t in losses)); count=len(trades)
    return {'trades':trades,'count':count,'wins':len(wins),'losses':len(losses),'winRate':len(wins)/count*100 if count else 0,'totalR':totalr,'expectancyR':totalr/count if count else 0,'profitFactor':grosswin/grossloss if grossloss else (None if grosswin else 0),'maxDrawdownPct':maxdd,'endingEquity':equity,'parameters':{'lookback':lookback,'rr':rr,'riskPct':risk_pct,'bodyMultiple':body_multiple,'maxRiskPct':max_risk_pct,'maxHoldingBars':max_holding,'spread':spread,'slippage':slippage},'warning':'Historical rule test only. Intra-candle ordering uses conservative stop-first handling. Results depend on data quality and assumptions; no profitability claim.'}

def multi_timeframe(sets):
    result={}; bullish=0; bearish=0
    for tf,bars in sets.items():
        if not bars: continue
        a=analyze(bars); result[tf]=a; bullish+=a['bias']=='bullish'; bearish+=a['bias']=='bearish'
    consensus='bullish' if bullish>bearish else 'bearish' if bearish>bullish else 'mixed/neutral'
    return {'timeframes':result,'consensus':consensus,'bullishCount':bullish,'bearishCount':bearish,'note':'Timeframe consensus is simple midpoint-based bias, not a predictive model.'}

def extract_concepts(content):
    text=content.lower(); patterns={'liquidity':['liquidity','equal highs','equal lows','buy-side liquidity','sell-side liquidity'],'sweep':['sweep','stop hunt','liquidity grab'],'market_structure':['bos','break of structure','mss','market structure shift','choch'],'fair_value_gap':['fvg','fair value gap','imbalance'],'displacement':['displacement','impulse'],'order_block':['order block','breaker block'],'premium_discount':['premium','discount'],'sessions':['killzone','london session','new york session','asia session'],'risk':['risk management','risk per trade','rr','risk reward']}
    return [k for k,terms in patterns.items() if any(t in text for t in terms)]
def researcher(knowledge,strategies,bt=None):
    concepts=sorted(set(c for k in knowledge for c in extract_concepts(k.get('content','')+' '+k.get('title','')))); rec=[]
    rec.append('For each strategy, specify objective trigger, stop logic, exit logic, session and invalidation before execution/backtesting.')
    if not concepts: rec.append('No recognized trading concepts found in indexed text. Add transcript text or notes, not only links.')
    if bt:
        if bt.get('count',0)<30:rec.append('Small sample (<30 trades): treat statistics as weak evidence.')
        if bt.get('expectancyR',0)<=0:rec.append('Observed expectancy is non-positive; avoid optimization until rule quality/data assumptions are reviewed.')
        else:rec.append('Positive expectancy in this historical sample only; validate on unseen data and include costs.')
    return {'concepts':concepts,'knowledgeCount':len(knowledge),'strategyCount':len(strategies),'recommendations':rec,'limitations':['Deterministic text extraction, not autonomous LLM learning.','Video links alone do not guarantee transcript access.','A strategy becomes executable only when explicit rules are configured.']}
def optimize(bars, risk_pct=1.0, max_risk_pct=3.0):
    """Small parameter grid with chronological holdout; optimize train segment, report unseen holdout."""
    if len(bars)<100: raise ValueError('Optimizer requires at least 100 candles for a meaningful chronological split')
    split=int(len(bars)*0.7); train=bars[:split]; test=bars[split:]; candidates=[]
    for lb in (3,5,8):
      for rr in (1.5,2.0,3.0):
       for bm in (1.0,1.25,1.5):
        r=backtest(train,lookback=lb,rr=rr,risk_pct=risk_pct,body_multiple=bm,max_risk_pct=max_risk_pct)
        candidates.append({'lookback':lb,'rr':rr,'bodyMultiple':bm,'trainTrades':r['count'],'trainExpectancyR':r['expectancyR'],'trainWinRate':r['winRate'],'trainProfitFactor':r['profitFactor']})
    candidates.sort(key=lambda x:(x['trainTrades']>=10,x['trainExpectancyR'],x['trainProfitFactor'] or 0),reverse=True)
    top=candidates[:5]; validated=[]
    for c in top:
      result=backtest(test,lookback=c['lookback'],rr=c['rr'],risk_pct=risk_pct,body_multiple=c['bodyMultiple'],max_risk_pct=max_risk_pct)
      validated.append({**c,'holdoutTrades':result['count'],'holdoutExpectancyR':result['expectancyR'],'holdoutWinRate':result['winRate'],'holdoutProfitFactor':result['profitFactor'],'holdoutMaxDrawdownPct':result['maxDrawdownPct']})
    validated.sort(key=lambda x:(x['holdoutTrades']>=5,x['holdoutExpectancyR']),reverse=True)
    return {'trainBars':len(train),'holdoutBars':len(test),'candidatesTested':len(candidates),'ranked':validated,'warning':'Chronological 70/30 split, not walk-forward. Parameter search can overfit; use larger data, costs and independent validation before trading.'}
