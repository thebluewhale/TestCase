import asyncio, base64, json, subprocess, tempfile, time, urllib.request
from pathlib import Path
from websockets.asyncio.client import connect

async def main():
    profile = tempfile.TemporaryDirectory(prefix='object-review-browser-', ignore_cleanup_errors=True)
    log = open('/tmp/object-review-browser.log','w')
    proc = subprocess.Popen(['/home/jh_marc.kim/.cache/ms-playwright/chromium-1248/chrome-linux64/chrome','--headless','--no-sandbox','--disable-dev-shm-usage','--no-first-run','--remote-debugging-port=0','--user-data-dir='+profile.name,'about:blank'],stdout=log,stderr=log)
    try:
        active = Path(profile.name)/'DevToolsActivePort'
        for _ in range(100):
            if active.exists():break
            await asyncio.sleep(.1)
        port=int(active.read_text().splitlines()[0])
        pages=json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/json/list'))
        async with connect(next(p for p in pages if p['type']=='page' and p['url']=='about:blank')['webSocketDebuggerUrl'],max_size=20_000_000) as ws:
            seq=0;errors=[]
            async def send(method,params=None):
                nonlocal seq
                seq+=1; ident=seq
                await ws.send(json.dumps({'id':ident,'method':method,'params':params or {}}))
                while True:
                    result=json.loads(await ws.recv())
                    if result.get('method')=='Runtime.exceptionThrown':errors.append(result)
                    if result.get('id')==ident:
                        if 'error' in result:raise RuntimeError(result['error'])
                        return result.get('result',{})
            async def js(code):
                r=await send('Runtime.evaluate',{'expression':code,'returnByValue':True,'awaitPromise':True})
                if 'exceptionDetails' in r:raise RuntimeError(r['exceptionDetails'])
                return r['result'].get('value')
            await send('Page.enable');await send('Runtime.enable')
            await send('Emulation.setDeviceMetricsOverride',{'width':1500,'height':1050,'deviceScaleFactor':1,'mobile':False})
            path=Path('/home/jh_marc.kim/TestCase/anomaly_benchmarks/index.html')
            await send('Page.navigate',{'url':path.as_uri()})
            for _ in range(100):
                if await js("document.querySelectorAll('#files tr').length===18"):break
                await asyncio.sleep(.1)
            assert await js("document.querySelectorAll('#files tr').length") == 18
            ids=await js("cases.map(c=>c.id)")
            for sid in ids:
                await js("document.querySelector('[data-id=\""+sid+"\"] button').click()")
                assert await js("document.querySelector('#input-name').textContent") == sid+'.mp4'
            await js("document.querySelector('[data-id=\"synthetic-cup-1-disappear\"] button').click()")
            for _ in range(100):
                if await js("input.readyState>=2 && pair.readyState>=2 && Array.from(document.querySelectorAll('.evidence img')).every(i=>i.complete && i.naturalWidth>0)"):break
                await asyncio.sleep(.1)
            assert await js("input.readyState>=2 && pair.readyState>=2")
            assert await js("document.querySelector('#selected-status').textContent.includes('찾음')")
            assert await js("document.querySelectorAll('.candidate').length") >= 1
            await js("seek(2.9)");await asyncio.sleep(.2)
            assert await js("Math.abs(input.currentTime-pair.currentTime)<.06")
            await js("play()");await asyncio.sleep(.35)
            assert await js("!input.paused && !pair.paused")
            await js("document.querySelector('#pause').click();seek(2.9)");await asyncio.sleep(.2)
            assert await js("document.querySelector('#region').style.display==='block'")
            assert await js("Array.from(document.querySelectorAll('.evidence img')).every(i=>i.complete && i.naturalWidth>0)")
            shot=await send('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})
            Path('/tmp/fresh-object-review-desktop.png').write_bytes(base64.b64decode(shot['data']))
            await js("document.querySelector('[data-id=\"synthetic-cup-1-position\"] button').click()")
            assert await js("document.querySelector('#selected-status').textContent.includes('놓침')")
            assert await js("document.querySelectorAll('.candidate').length") == 0
            for sid in ('original-cup-1','original-hand-2'):
                await js("document.querySelector('[data-id=\""+sid+"\"] button').click()")
                assert await js("document.querySelector('#pair-player').hidden")
                assert await js("document.querySelector('#expected').textContent.includes('정답이 없는')")
                assert not await js("document.querySelector('#selected-status').textContent.includes('사람 확인 정상')")
            await js("document.querySelector('[data-id=\"synthetic-hand-2-steady\"] button').click()")
            assert await js("document.querySelector('#no-pair').textContent.includes('자체가')")
            for label,count in [('합성 결함',8),('정상 대조',8),('원본',2)]:
                await js("document.querySelector('#filter').value="+json.dumps(label)+";document.querySelector('#filter').dispatchEvent(new Event('change'))")
                assert await js("document.querySelectorAll('#files tr').length") == count
            await send('Emulation.setDeviceMetricsOverride',{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True})
            assert await js("document.documentElement.scrollWidth<=390")
            assert not errors,errors
            print(json.dumps({'file_selection':18,'positive_filter':8,'control_filter':8,'original_filter':2,'paired_video_play_seek_pause':'passed','candidate_evidence':'passed','missed_defect_presentation':'passed','unlabeled_original_presentation':'passed','mobile_overflow':'none','javascript_errors':len(errors)}))
    finally:
        proc.terminate();proc.wait(timeout=10);log.close();profile.cleanup()
asyncio.run(main())
