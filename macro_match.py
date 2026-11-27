"""Conservative matching: candidates only, explicit reference period required."""
from macro_metrics import calculate
from datetime import datetime
MAPPING={"CPI m/m":"cpi_sa_mom_pct","CPI y/y":"cpi_nsa_yoy_pct","Non-Farm Employment Change":"nfp_change_thousands","Unemployment Rate":"unemployment_pct"}
def candidate(event,rows,period,now):
    if event.get("currency")!="USD" or event.get("impact")!="high" or event.get("title") not in MAPPING: return None
    if now.tzinfo is None or datetime.fromisoformat(event["date"])>now: return None
    value=calculate(rows,period)["metrics"][MAPPING[event["title"]]]
    if value is None: return None
    return {"event_id":event["id"],"reference_period":period,"metric":MAPPING[event["title"]],"candidate_value":value,"source":"BLS","release_verified":False,"review_required":True}
