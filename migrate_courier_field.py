
import db

def migrate():
    items = db.list_tracked()
    updated = 0
    for item in items:
        # Prefer the DB field, fallback to last_result if present
        courier = item.get("courier") or (item.get("last_result") or {}).get("courier")
        std_courier = db.standardize_courier_name(courier)
        if std_courier and std_courier != courier:
            db.update_tracked_courier(item["id"], std_courier)
            updated += 1
    print(f"Migration complete. {updated} records updated.")

if __name__ == "__main__":
    migrate()
