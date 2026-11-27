import unittest
from macro_metrics import calculate
class MetricsTests(unittest.TestCase):
    def test_metrics(self):
        rows=[dict(series=s,period=p,value=v) for s,p,v in [("CUSR0000SA0","2026-01","303"),("CUSR0000SA0","2025-12","300"),("CUUR0000SA0","2026-01","312"),("CUUR0000SA0","2025-01","300"),("CES0000000001","2026-01","160100"),("CES0000000001","2025-12","160000"),("LNS14000000","2026-01","4.1")]]
        self.assertEqual(calculate(rows,"2026-01")["metrics"],dict(cpi_sa_mom_pct="1.0",cpi_nsa_yoy_pct="4.0",nfp_change_thousands="100.0",unemployment_pct="4.1"))
    def test_missing(self):
        self.assertTrue(all(v is None for v in calculate([],"2026-01")["metrics"].values()))
