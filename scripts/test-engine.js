const fs=require('fs'),vm=require('vm'),src=fs.readFileSync('app.js','utf8');
const sweep=src.slice(src.indexOf('function sweepSignal'),src.indexOf('function runBT'));
const bt=src.slice(src.indexOf('function runBT'),src.indexOf('function displayResults'));
const context={state:{data:{}},Math,Number};vm.createContext(context);vm.runInContext(sweep+bt,context);
const bars=[];for(let i=0;i<10;i++)bars.push({t:String(i),o:9.5,h:10,l:9,c:9.5});bars.push({t:'sweep',o:9.5,h:11,l:9.3,c:9.4});bars.push({t:'target',o:9.4,h:9.6,l:6.1,c:6.5});
context.state.data['EURUSD_M5']={bars};const r=context.runBT('EURUSD','M5',5,2);
if(r.trades.length!==1||r.trades[0].resultR!==2||r.wins!==1||r.winrate!==100)throw new Error('Backtest fixture failed: '+JSON.stringify(r));
const sig=context.sweepSignal(bars.slice(0,11),5,2);if(!sig||sig.direction!=='SELL')throw new Error('Signal fixture failed');
console.log('Backtest fixture: PASS (one sell sweep trade, +2R TP)');
