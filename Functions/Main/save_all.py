from Classes import database_class

def save_all(
        original_db: database_class.Database, 
        chosen_db: database_class.Database, 
        cleaned_db: database_class.Database, 
        prepared_db: database_class.Database, 
        final_db: database_class.Database
        ) -> None:
    
    base = r"C:\Users\kwinw\OneDrive\Desktop\Junior S1\Yang. Lab\Structured Database for 2D Materials\Databases"

    db_files = {
        "original_database.json": original_db,
        "chosen_database.json":   chosen_db,
        "cleaned_database.json":  cleaned_db,
        "prepared_database.json": prepared_db,
        "final_database.json":    final_db,
    }

    for filename, db in db_files.items():
        db.save(f"{base}\\{filename}")

    print("All databases saved.")
