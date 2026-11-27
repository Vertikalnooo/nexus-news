"""Calculate period-specific BLS metrics; never infer release verification."""
from decimal import Decimal, ROUND_HALF_UP
def calculate(rows, period):
    year,month=map(int,period.split("-"))
    prev=f"{year-(month==1):04}-{12 if month==1 else month-1:02}"
    annual=f"{year-1:04}-{month:02}"
    values={}
    for r in rows:
        key=(r["series"],r["period"])
        value=Decimal(r["value"])
        if not value.is_finite(): raise ValueError("nonfinite")
        if key in values and values[key]!=value: raise ValueError("conflicting observations")
        values[key]=value
    out={}
    def get(series,p): return values.get((series,p))
    def change(series,p,percent):
        a,z=get(series,period),get(series,p)
        if a is None or z is None or (percent and z<=0): return None
        return str(((a/z-1)*100 if percent else a-z).quantize(Decimal("0.1"),rounding=ROUND_HALF_UP))
    out["cpi_sa_mom_pct"]=change("CUSR0000SA0",prev,True)
    out["cpi_nsa_yoy_pct"]=change("CUUR0000SA0",annual,True)
    out["nfp_change_thousands"]=change("CES0000000001",prev,False)
    u=get("LNS14000000",period)
    out["unemployment_pct"]=str(u) if u is not None else None
    return {"period":period,"metrics":out,"release_verified":False}
