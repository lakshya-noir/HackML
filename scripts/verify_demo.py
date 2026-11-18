"""Verify UI assets, CORS, fresh inference and response shapes on a running demo."""
import argparse
import json
from pathlib import Path
import urllib.request
import urllib.error

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--api',default='http://127.0.0.1:8000')
ap.add_argument('--ui',default='http://127.0.0.1:5500')
a=ap.parse_args()
def request(path,body=None):
    req=urllib.request.Request(a.api+path,data=json.dumps(body).encode() if body else None,
        headers={'Content-Type':'application/json','Origin':a.ui})
    with urllib.request.urlopen(req,timeout=300) as response:
        assert response.headers.get('Access-Control-Allow-Origin')=='*'
        return json.load(response)

for asset in ['/','/vendor/leaflet/leaflet.js','/vendor/leaflet/leaflet.css']:
    with urllib.request.urlopen(a.ui+asset,timeout=10) as response:
        assert response.status==200 and len(response.read())>100
req=urllib.request.Request(a.api+'/predict',method='OPTIONS',headers={
    'Origin':a.ui,'Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'content-type'})
with urllib.request.urlopen(req) as response:
    assert response.status==200 and response.headers.get('Access-Control-Allow-Origin')=='*'
health=request('/health'); assert health['model_loaded']
trips=request('/trips')['trips']; assert len(trips)==10
out={'scope':'local HTTP checks; not a browser render or physical two-laptop test',
     'api':a.api,'ui':a.ui,'model_loaded':True,'ui_assets_and_cors':'passed','trips':[]}
for trip in trips:
    result=request('/predict',{'trip_id':trip['trip_id'],'fresh':True})
    assert not result['cached']
    assert len(result['observation_arc_ids'])==len(result['gps_lonlat'])==result['n_observations']
    assert result['route_geojson']['type']=='MultiLineString'
    assert 'reference_route' not in result and 'reference_arc_ids' not in result
    out['trips'].append({k:result[k] for k in ['trip_id','n_observations','cached','timing_ms','metrics']})
    print(result['trip_id'],'fresh prediction and geometry/observation counts passed',flush=True)
try:
    request('/predict',{'trip_id':'not-a-trip','fresh':True})
    raise AssertionError('Expected 404')
except urllib.error.HTTPError as e:
    assert e.code==404
out['unknown_trip_404']='passed'
Path('results/api_verification_local.json').write_text(json.dumps(out,indent=2))
print('10/10 fresh predictions, static assets, CORS and 404 check passed; evidence saved.')
