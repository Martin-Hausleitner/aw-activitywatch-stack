#!/usr/bin/env python3
import argparse, collections, datetime as dt, json, urllib.parse, urllib.request
from zoneinfo import ZoneInfo

BASE='http://127.0.0.1:5600/api/0'
TZ=ZoneInfo(args.timezone)

def api(path, params=None):
    url=BASE+path
    if params:
        url += '?' + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.load(r)

def parse(ts): return dt.datetime.fromisoformat(ts.replace('Z','+00:00'))
def qbid(bid): return urllib.parse.quote(bid, safe='')
def overlap(a,b,c,d):
    return max(0, (min(b,d)-max(a,c)).total_seconds())

def newest_bucket(buckets, prefix, typ=None):
    c=[b for b,v in buckets.items() if b.startswith(prefix) and (typ is None or v.get('type')==typ)]
    if not c: return None
    return max(c, key=lambda b: buckets[b].get('last_updated') or buckets[b].get('created') or '')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--days', type=int, default=14)
    args=ap.parse_args()
    end=dt.datetime.now(dt.timezone.utc)
    start=end-dt.timedelta(days=args.days)
    buckets=api('/buckets/')
    afk=newest_bucket(buckets,'aw-watcher-afk_','afkstatus')
    win=newest_bucket(buckets,'aw-watcher-window_','currentwindow')
    print('Buckets:', {'afk':afk,'window':win})
    if not afk: raise SystemExit('No AFK bucket found')
    params={'start':start.isoformat(), 'end':end.isoformat()}
    afks=sorted(api(f'/buckets/{qbid(afk)}/events', params), key=lambda e:e['timestamp'])
    wins=sorted(api(f'/buckets/{qbid(win)}/events', params), key=lambda e:e['timestamp']) if win else []
    by=collections.defaultdict(lambda:{'active':0,'before9':0,'after18':0,'first':None,'last':None,'apps':collections.Counter()})
    for e in afks:
        if e.get('duration',0)<=0 or e.get('data',{}).get('status')!='not-afk': continue
        a=parse(e['timestamp']); b=a+dt.timedelta(seconds=e['duration'])
        cur=a
        while cur<b:
            loc=cur.astimezone(TZ); day=loc.date()
            nxt=min(b, dt.datetime.combine(day+dt.timedelta(days=1), dt.time(), TZ).astimezone(dt.timezone.utc))
            sec=(nxt-cur).total_seconds(); r=by[day]
            r['active']+=sec; r['first']=min(r['first'],loc) if r['first'] else loc; r['last']=max(r['last'],nxt.astimezone(TZ)) if r['last'] else nxt.astimezone(TZ)
            r['before9']+=overlap(cur,nxt,dt.datetime.combine(day,dt.time(),TZ).astimezone(dt.timezone.utc),dt.datetime.combine(day,dt.time(9),TZ).astimezone(dt.timezone.utc))
            r['after18']+=overlap(cur,nxt,dt.datetime.combine(day,dt.time(18),TZ).astimezone(dt.timezone.utc),dt.datetime.combine(day+dt.timedelta(days=1),dt.time(),TZ).astimezone(dt.timezone.utc))
            cur=nxt
    for e in wins:
        if e.get('duration',0)<=0: continue
        app=e.get('data',{}).get('app','?')
        if app == 'loginwindow': continue
        by[parse(e['timestamp']).astimezone(TZ).date()]['apps'][app]+=e['duration']
    days=[(d,r) for d,r in sorted(by.items()) if r['active']>=600]
    for d,r in days:
        print(d.isoformat(), f"active={r['active']/3600:.2f}h", f"first={r['first']:%H:%M}", f"last={r['last']:%H:%M}", f"<9={r['before9']/3600:.2f}h", f">18={r['after18']/3600:.2f}h", 'top=', [(a,round(s/3600,1)) for a,s in r['apps'].most_common(5)])
    work=[r for d,r in days if d.weekday()<5]
    wknd=[r for d,r in days if d.weekday()>=5]
    def avg(xs,k): return sum(x[k] for x in xs)/len(xs)/3600 if xs else 0
    print('Summary:', {'days':len(days),'weekday_avg_h':round(avg(work,'active'),2),'weekend_avg_h':round(avg(wknd,'active'),2),'weekday_after18_h':round(avg(work,'after18'),2),'weekend_days':len(wknd)})

if __name__=='__main__': main()
