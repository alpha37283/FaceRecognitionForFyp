#!/usr/bin/env python3
import psycopg2
import os
import sys
from backend.config import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD


def view_database():
    """View contents of PostgreSQL database"""
    
    try:
        # Connect to database
        # For peer authentication, try connecting without password first
        # If that fails, it means we need password or sudo access
        try:
            if POSTGRES_PASSWORD:
                conn = psycopg2.connect(host=POSTGRES_HOST, port=POSTGRES_PORT, database=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PASSWORD)
            else:
                conn = psycopg2.connect(host=POSTGRES_HOST, port=POSTGRES_PORT, database=POSTGRES_DB, user=POSTGRES_USER)
        except psycopg2.OperationalError as e:
            if "password" in str(e).lower() or "authentication" in str(e).lower():
                import getpass
                current_user = getpass.getuser()
                conn = psycopg2.connect(host=POSTGRES_HOST, port=POSTGRES_PORT, database=POSTGRES_DB, user=current_user)
            else:
                raise
        
        cursor = conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cursor.fetchall()
        
        if not tables:
            print("[-] Database exists but no tables found")
            print("[INFO] Tables will be created when backend API starts")
            conn.close()
            return
        
        print("=" * 70)
        print("POSTGRESQL DATABASE CONTENTS")
        print("=" * 70)
        
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
        
        print("\n🔢 FACE_EMBEDDINGS TABLE")
        print("-" * 70)
        cursor.execute("SELECT embedding_id, person_id, source_image_url, detection_method, confidence_score, created_at FROM face_embeddings")
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
        
        print("\n📝 SYNC LOG TABLE")
        print("-" * 70)
        cursor.execute("SELECT * FROM embedding_sync_log")
        logs = cursor.fetchall()
        if logs:
            print(f"{'Sync ID':<8} {'Emb ID':<8} {'Person ID':<10} {'Action':<10} {'Timestamp'}")
            print("-" * 70)
            for log in logs:
                sync_id, emb_id, person_id, action, timestamp, synced = log
                action_str = action.value if hasattr(action, 'value') else str(action)
                print(f"{sync_id:<8} {emb_id:<8} {person_id:<10} {action_str:<10} {timestamp}")
        else:
            print("(No sync logs)")
        
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
        
    except psycopg2.OperationalError as e:
        print(f"[-] Database connection error: {e}")
        print("[INFO] Make sure PostgreSQL is running and database exists")
        print("[INFO] Run: ./create_postgres_db.sh")
    except Exception as e:
        print(f"[-] Error: {e}")


if __name__ == "__main__":
    view_database()

