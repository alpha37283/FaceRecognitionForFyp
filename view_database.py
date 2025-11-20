#!/usr/bin/env python3
"""
Simple script to view database contents
"""
import sqlite3
import os
import sys

def view_database(db_path="data/database/face_system.db"):
    """View contents of SQLite database"""
    
    if not os.path.exists(db_path):
        print(f"[-] Database file not found: {db_path}")
        print("[INFO] Database will be created when you first upload an embedding")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if not tables:
            print("[-] Database exists but no tables found")
            print("[INFO] Tables will be created when backend API starts")
            conn.close()
            return
        
        print("=" * 70)
        print("DATABASE CONTENTS")
        print("=" * 70)
        
        # View persons table
        print("\n📋 PERSONS TABLE")
        print("-" * 70)
        cursor.execute("SELECT * FROM persons")
        persons = cursor.fetchall()
        if persons:
            print(f"{'ID':<5} {'Name':<20} {'Age':<5} {'Gender':<10} {'Created At'}")
            print("-" * 70)
            for person in persons:
                person_id, name, age, gender, notes, created_at, updated_at = person
                age_str = str(age) if age else "N/A"
                gender_str = gender if gender else "N/A"
                print(f"{person_id:<5} {name:<20} {age_str:<5} {gender_str:<10} {created_at}")
        else:
            print("(No persons in database)")
        
        # View embeddings table (without vector)
        print("\n🔢 FACE_EMBEDDINGS TABLE")
        print("-" * 70)
        cursor.execute("""
            SELECT embedding_id, person_id, source_image_url, 
                   detection_method, confidence_score, created_at 
            FROM face_embeddings
        """)
        embeddings = cursor.fetchall()
        if embeddings:
            print(f"{'Emb ID':<8} {'Person ID':<10} {'Method':<10} {'Confidence':<12} {'Image'}")
            print("-" * 70)
            for emb in embeddings:
                emb_id, person_id, img_url, method, conf, created = emb
                method_str = method if method else "N/A"
                conf_str = f"{conf:.2f}" if conf else "N/A"
                img_name = os.path.basename(img_url) if img_url else "N/A"
                print(f"{emb_id:<8} {person_id:<10} {method_str:<10} {conf_str:<12} {img_name}")
        else:
            print("(No embeddings in database)")
        
        # View sync log
        print("\n📝 SYNC LOG TABLE")
        print("-" * 70)
        cursor.execute("SELECT * FROM embedding_sync_log")
        logs = cursor.fetchall()
        if logs:
            print(f"{'Sync ID':<8} {'Emb ID':<8} {'Person ID':<10} {'Action':<10} {'Timestamp'}")
            print("-" * 70)
            for log in logs:
                sync_id, emb_id, person_id, action, timestamp, synced = log
                print(f"{sync_id:<8} {emb_id:<8} {person_id:<10} {action.value:<10} {timestamp}")
        else:
            print("(No sync logs)")
        
        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        cursor.execute("SELECT COUNT(*) FROM persons")
        person_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM face_embeddings")
        embedding_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM embedding_sync_log")
        log_count = cursor.fetchone()[0]
        
        print(f"Total Persons: {person_count}")
        print(f"Total Embeddings: {embedding_count}")
        print(f"Total Sync Logs: {log_count}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"[-] Database error: {e}")
    except Exception as e:
        print(f"[-] Error: {e}")


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "data/database/face_system.db"
    view_database(db_path)

