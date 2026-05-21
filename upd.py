import json, os  
f=open(r'C:\Users\15206\.qclaw\workspace\memory\heartbeat-state.json','r',encoding='utf-8')  
d=json.load(f)  
d['lastChecks']['rss_music']='2026-05-02'  
f.close()  
f=open(r'C:\Users\15206\.qclaw\workspace\memory\heartbeat-state.json','w',encoding='utf-8')  
json.dump(d,f,ensure_ascii=False)  
f.close()  
