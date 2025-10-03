from Classes import database_class
from Classes import report_class

def edit_paper(
        *,
        target_db: database_class.Database,
) -> None:
    
    while True:
        doi = input("Enter DOI (enter to cancel): ").strip()
        if not doi:
            return
        
        report: report_class.Report = target_db.get(doi)

        print("\n")

        if report is None:
            print("Error: Report not found in this database")
            continue
        
        print(f"This is the searched report data in {target_db.name}")
        print(f"    DOI: {report.DOI}")
        print(f"    Title: {report.title}")
        print(f"    Link: {report.link}")
        print(f"    Notes: {report.notes}")
        print(f"    Text: {report.text} \n")
        break

    banned_attr = { # lower case to match user input
        "doi",
        "title",
        "link",
    }

    acceptable_attr = [
        "notes",
        "text",
    ]

    while True:
        attribute = input("Please enter one of these attributes to edit (notes/text), or enter to cancel: ").strip().lower()
        if not attribute:
            return

        if attribute in banned_attr:
            print("Chosen function is immutable and not allowed for editing")
            continue

        elif attribute in acceptable_attr:
            if attribute == "notes":
                note = input("Please enter the notes you would like to add").strip()
                report.add_notes(note)
                return
            else:
                texts = input("Please enter the text you would like to add").strip()
                report.attach_text(texts)
                return
        else:
            print("Error: input is not a valid attribute")
            continue
    