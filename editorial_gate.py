"""Independent review gate; never authorizes actual publication."""
import re
def eligible_for_review(original, translated):
    if not isinstance(original,str) or not isinstance(translated,str): return False
    if not translated.strip() or re.search(r"конюшн|преступник|загадк|антропическ|символизирован",translated,re.I): return False
    # Conservative: missing or added numeric literals require review.
    return sorted(re.findall(r"\d+",original))==sorted(re.findall(r"\d+",translated))
def publication_eligible(draft):
    # No trusted editorial approval mechanism yet.
    return False
