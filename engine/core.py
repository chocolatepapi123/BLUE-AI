"""Deterministic BLUE AI trading research engine. No external API required."""
from __future__ import annotations
import csv, io, json, math, statistics, re
from datetime import datetime


def load_csv(text):
    rows=[]
    reader=csv.DictReader(io.StringIO(text))
    if not reader.fieldnames: raise ValueError('CSV must include headers')
    aliases={'time':['time','timestamp','date','datetime'],'open':['open','o'],'high':['high','h'],'low':['low','l'],'close':['close','c'],'volume':['volume','vol','v']}
    mapping={}
    for key,names in aliases.items():
        for h in reader.fieldnames:
            if h.lower().strip() in names: mapping[key]=h; break
    missing=[k for k in ['open','high','low','close'] if k not in mapping]
    if missing: raise ValueError('Missing required CSV columns: '+', '.join(missing))
    for r in reader:
        try:
            bar={k:float(r[mapping[k]]) for k in ['open','high','low','close']}
            bar['time']=r.get(mapping.get('time',''), '') if mapping.get('time') else str(len(rows))
            bar['volume']=float(r[mapping['volume']]) if mapping.get('volume') and r.get(mapping['volume']) else 0
            if bar['high'] < bar['low'] or bar['high'] < max(bar['open'],bar['close']) or bar['low'] > min(bar['open'],bar['close']): continue
            rows.append(bar)
        except (ValueError,TypeError): continue
    if len(rows)<10: raise ValueError(f'Need at least 10 valid candles; found {len(rows)}')
    return rows


def pivots(bars, left=2, right=2):
    highs=[]; lows=[]
    for i in range(left, len(bars)-right):
        h=bars[i]['high']; l=bars[i]['low']
        if all(h>bars[j]['high'] for j in range(i-left,i)) and all(h>=bars[j]['high'] for j in range(i+1,i+right+1)): highs.append((i,h))
        if all(l<bars[j]['low'] for j in range(i-left,i)) and all(l<=bars[j]['low'] for j in range(i+1,i+right+1)): lows.append((i,l))
    return highs,lows


def analyze(bars):
    highs,lows=pivots(bars)
    last=bars[-1]; recent=bars[-20:]
    swing_high=highs[-1][1] if highs else max(b['high'] for b in bars[-10:])
    swing_low=lows[-1][1] if lows else min(b['low'] for b in bars[-10:])
    prev_high=max(b['high'] for b in bars[-6:-1]); prev_low=min(b['low'] for b in bars[-6:-1])
    sweep_high=last['high']>prev_high and last['close']<prev_high
    sweep_low=last['low']<prev_low and last['close']>prev_low
    avg_body=statistics.mean(abs(b['close']-b['open']) for b in bars[-20:-1]) or 1e-9
    body=abs(last['close']-last['open']); displacement=body>=avg_body*1.5
    fvg=None
    if len(bars)>=3:
        a,b,c=bars[-3:]
        if a['high']<c['low']: fvg={'type':'bullish','low':a['high'],'high':c['low']}
        elif a['low']>c['high']: fvg={'type':'bearish','low':c['high'],'high':a['low']}
    bias='bullish' if last['close']>swing_low+(swing_high-swing_low)*0.55 else ('bearish' if last['close']<swing_low+(swing_high-swing_low)*0.45 else 'neutral')
    signals=[]
    if sweep_low and displacement and last['close']>last['open']: signals.append({'direction':'BUY','reason':'Recent low sweep + bullish displacement','score':70+(15 if fvg and fvg['type']=='bullish' else 0)})
    if sweep_high and displacement and last['close']<last['open']: signals.append({'direction':'SELL','reason':'Recent high sweep + bearish displacement','score':70+(15 if fvg and fvg['type']=='bearish' else 0)})
    return {'price':last['close'],'time':last['time'],'bias':bias,'swingHigh':swing_high,'swingLow':swing_low,'sweepHigh':sweep_high,'sweepLow':sweep_low,'displacement':displacement,'avgBody':avg_body,'lastBody':body,'fvg':fvg,'signals':signals,'pivotHighs':highs[-8:],'pivotLows':lows[-8:]}


def backtest(bars, lookback=5, rr=2.0, risk_pct=1.0):
    trades=[]; equity=100.0; peak=equity; maxdd=0.0
    for i in range(max(lookback+3,10),len(bars)-1):
        hist=bars[:i+1]; cur=hist[-1]; prev=hist[-lookback-1:-1]
        ph=max(b['high'] for b in prev); pl=min(b['low'] for b in prev)
        avgbody=statistics.mean(abs(b['close']-b['open']) for b in hist[-20:-1]) or 1e-9
        body=abs(cur['close']-cur['open'])
        side=None
        if cur['low']<pl and cur['close']>pl and cur['close']>cur['open'] and body>=avgbody*1.25: side='long'
        elif cur['high']>ph and cur['close']<ph and cur['close']<cur['open'] and body>=avgbody*1.25: side='short'
        if not side: continue
        entry=cur['close']; stop=cur['low'] if side=='long' else cur['high']; risk=abs(entry-stop)
        if risk<=0 or risk/entry>0.03: continue
        tp=entry+risk*rr if side=='long' else entry-risk*rr
        outcome=None; exitprice=None; exitidx=None
        for j in range(i+1,min(i+80,len(bars))):
            b=bars[j]
            stop_hit=b['low']<=stop if side=='long' else b['high']>=stop
            tp_hit=b['high']>=tp if side=='long' else b['low']<=tp
            if stop_hit: outcome=-1; exitprice=stop; exitidx=j; break # conservative stop first
            if tp_hit: outcome=rr; exitprice=tp; exitidx=j; break
        if outcome is None: continue
        trades.append({'side':side,'entryTime':cur['time'],'exitTime':bars[exitidx]['time'],'entry':entry,'stop':stop,'target':tp,'r':outcome})
        equity*=1+(risk_pct/100)*outcome; peak=max(peak,equity); maxdd=max(maxdd,(peak-equity)/peak*100)
    wins=sum(t['r']>0 for t in trades); losses=sum(t['r']<0 for t in trades)
    totalr=sum(t['r'] for t in trades); avg=totalr/len(trades) if trades else 0
    grosswin=sum(t['r'] for t in trades if t['r']>0); grossloss=abs(sum(t['r'] for t in trades if t['r']<0))
    return {'trades':trades,'count':len(trades),'wins':wins,'losses':losses,'winRate':wins/len(trades)*100 if trades else 0,'totalR':totalr,'expectancyR':avg,'profitFactor':grosswin/grossloss if grossloss else (float('inf') if grosswin else 0),'maxDrawdownPct':maxdd,'endingEquity':equity,'parameters':{'lookback':lookback,'rr':rr,'riskPct':risk_pct},'warning':'Illustrative rule-based historical test. No spread, slippage, commissions, or intra-candle execution uncertainty modeled.'}


def researcher(knowledge, strategy, backtest_result=None):
    text=' '.join((k.get('content','') for k in knowledge)).lower()
    tags=sorted(set(re.findall(r'\b(?:liquidity|sweep|bos|mss|fvg|fair value gap|displacement|order block|premium|discount|killzone|risk|rr|ict|smc)\b',text)))
    report={'extractedConcepts':tags,'knowledgeItems':len(knowledge),'strategyCount':len(strategy),'recommendations':[],'limitations':[]}
    if not tags: report['recommendations'].append('Add transcripts or notes with specific entry, invalidation, and management rules; concept extraction found no recognized terms.')
    report['recommendations'].append('Convert each concept into a falsifiable rule: trigger, stop placement, target, session, timeframe, and invalidation.')
    if backtest_result:
        if backtest_result['count']<30: report['recommendations'].append('Sample is small (<30 trades); do not draw performance conclusions.')
        if backtest_result['expectancyR']<=0: report['recommendations'].append('Current test expectancy is non-positive; inspect setup quality before optimizing.')
        else: report['recommendations'].append('Positive historical expectancy detected, but validate out-of-sample and include execution costs before trusting it.')
    report['limitations']=['This module uses deterministic text matching and metrics, not a hosted LLM. It does not autonomously rewrite strategy rules.']
    return report
