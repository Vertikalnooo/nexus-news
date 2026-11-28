"""Official BLS observations, not automatically matched to calendar releases."""
import json
from decimal import Decimal
from urllib.request import Request,build_opener
from collector import NoRedirect
SERIES={"CPI":"CUSR0000SA0","CPI_NSA":"CUUR0000SA0","NFP":"CES0000000001","UNEMPLOYMENT":"LNS14000000"}
def fetch_observations():
    req=Request("https://api.bls.gov/publicAPI/v2/timeseries/data/",data=json.dumps({"seriesid":list(SERIES.values())}).encode(),headers={"Content-Type":"application/json"},method="POST")
    with build_opener(NoRedirect()).open(req,timeout=20) as response:
        raw=response.read(2_000_001)
    return parse_observations(raw)
def parse_observations(raw):
    if len(raw)>2_000_000: raise ValueError("oversize")
    obj=json.loads(raw)
    if obj.get("status")!="REQUEST_SUCCEEDED": raise ValueError("BLS failed")
    out=[]
    for series in obj["Results"]["series"]:
        if series["seriesID"] not in SERIES.values(): continue
        for row in series["data"]:
            period=row["period"]
            if period not in [f"M{i:02}" for i in range(1,13)]: continue
            try:
                value=Decimal(row["value"])
                if not value.is_finite(): continue
                year=int(row["year"])
            except (ValueError,ArithmeticError): continue
            out.append({"series":series["seriesID"],"period":f"{year:04}-{period[1:]}","value":str(value),"source":"BLS","release_verified":False})
    return out
if __name__=="__main__":
    rows=fetch_observations()
    print(json.dumps({"observations":len(rows),"series":sorted({r["series"] for r in rows})}))
    if not rows: raise SystemExit(1)
