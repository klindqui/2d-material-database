from Classes import database_class
from Functions.Helper import report_print

def db_reports_list(
        *,
        target_db: database_class.Database,
):
    
    reports = target_db.list()

    if not reports:
        print(f"\n {target_db.name} is empty.")
        return []

    print(f"\n Reports in {target_db.name}:")
    for r in reports:
        report_print.print_report(r)
        print("\n")
    return reports