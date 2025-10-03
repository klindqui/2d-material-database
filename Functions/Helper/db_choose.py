
from typing import Optional, Tuple
from Classes import database_class

def db_choose(
         *, 
        original_db: database_class.Database, 
        chosen_db: database_class.Database, 
        cleaned_db: database_class.Database, 
        prepared_db: database_class.Database, 
        final_db: database_class.Database
) -> Optional[Tuple[database_class.Database, Optional[database_class.Database]]]:
    
    for arg_name, db in {
        "original_db": original_db,
        "chosen_db":   chosen_db,
        "cleaned_db":  cleaned_db,
        "prepared_db": prepared_db,
        "final_db":    final_db,
    }.items():
        if not isinstance(db, database_class.Database):
            raise TypeError(f"{arg_name} must be a Database, got {type(db).__name__}")

    while True:
        print("\nAvailable databases: ")
        print("1. Original Database")
        print("2. Chosen Database")
        print("3. Cleaned Database")
        print("4. Prepared Database")
        print("5. Final Database")

        db_choice = input("Enter the database number: \n").strip()
        if not db_choice:
            return
        
        # choose your database
        db_map = {
            "1": (original_db, None),
            "2": (chosen_db,   original_db),
            "3": (cleaned_db,  chosen_db),
            "4": (prepared_db, cleaned_db),
            "5": (final_db,    prepared_db),
        }

        pair = db_map.get(db_choice)
        if pair is None:
            print("Invalid database choice. Try again.")
            continue

        target_db, previous_db = pair
        return (target_db, previous_db)
