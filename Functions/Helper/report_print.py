# report print (repetitive)
from Classes import report_class

def print_report(r: report_class.Report):
    print("DOI: ", r.DOI)
    print("Title: ", r.title)
    print("Link: ", r.link)
    if r.notes: print("Notes: ", r.notes)
    if r.text: print("Text :", (r.text[:80] + "...") if len(r.text or "") > 80 else r.text)