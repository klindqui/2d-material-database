from Classes import database_class

def doi_search(
        *, 
        original_db: database_class.Database, 
        chosen_db: database_class.Database, 
        cleaned_db: database_class.Database, 
        prepared_db: database_class.Database, 
        final_db: database_class.Database
):
    
    dbs = [
        original_db,
        chosen_db,
        cleaned_db,
        prepared_db,
        final_db
    ]

    doi = input("Enter DOI (enter to cancel): ").strip()
    if not doi:
        return

    for db in dbs:
        if db.contains_doi(doi):
            results = db.info(doi)
            doi_result, title, link = results
            print(f"Results in {db.name}: ")
            print(f"    DOI: {doi_result}")
            print(f"    Title: {title}")
            print(f"    Link: {link}")
        else:
            print(f"This database, {db.name}, does not contain the DOI {doi}")