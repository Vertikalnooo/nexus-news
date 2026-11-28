class GeminiBudget:
    def __init__(self,db): self.db=db
    def reserve(self):
        if not self.db.autocommit: raise ValueError("dedicated autocommit connection required")
        from psycopg.pq import TransactionStatus
        if self.db.info.transaction_status != TransactionStatus.IDLE: raise ValueError("outer transaction forbidden")
        with self.db.transaction():
            return self.db.execute("SELECT nexus.reserve_gemini()").fetchone()[0] is True
