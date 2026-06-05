import os
import sys
import gzip
import json
import time
import urllib.request
import sqlite3

CONCEPTNET_URL = "https://s3.amazonaws.com/conceptnet/downloads/2019/edges/conceptnet-assertions-5.7.0.csv.gz"
DOWNLOAD_PATH = "data/conceptnet-assertions-5.7.0.csv.gz"
DB_PATH = "data/conceptnet_offline.db"

def download_file(url, dest):
    print(f"Starting download of ConceptNet assertions dump from {url}...")
    start_time = time.time()
    
    # Custom progress reporter
    def report_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100.0, (downloaded / total_size) * 100)
            downloaded_mb = downloaded / (1024 * 1024)
            total_mb = total_size / (1024 * 1024)
            # Print every ~5% or at the end to keep console clean but informative
            if block_num % 1000 == 0 or downloaded >= total_size:
                sys.stdout.write(f"\rDownloading: {percent:.2f}% ({downloaded_mb:.1f} MB / {total_mb:.1f} MB)")
                sys.stdout.flush()
        else:
            downloaded_mb = downloaded / (1024 * 1024)
            sys.stdout.write(f"\rDownloading: {downloaded_mb:.1f} MB")
            sys.stdout.flush()

    # Ensure data directory exists
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    
    try:
        urllib.request.urlretrieve(url, dest, reporthook=report_hook)
        print(f"\nDownload completed successfully in {time.time() - start_time:.2f} seconds.")
    except Exception as e:
        print(f"\nError during download: {e}")
        raise e

def import_to_sqlite(gz_path, db_path):
    print("Initializing SQLite database...")
    if os.path.exists(db_path):
        print(f"Removing existing database file {db_path}...")
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # SQLite performance tuning
    cursor.execute("PRAGMA synchronous = OFF;")
    cursor.execute("PRAGMA journal_mode = MEMORY;")
    cursor.execute("PRAGMA page_size = 4096;")
    cursor.execute("PRAGMA cache_size = -1000000;")  # 1GB cache size
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assertions (
            relation TEXT,
            start TEXT,
            end TEXT,
            weight REAL
        )
    """)
    conn.commit()
    
    print("Processing ConceptNet assertions (filtering out Hebrew)...")
    start_time = time.time()
    count = 0
    inserted_count = 0
    batch = []
    batch_size = 100000
    
    try:
        # Open gzip stream
        with gzip.open(gz_path, 'rb') as f:
            for line in f:
                count += 1
                
                # Check for Hebrew '/c/he/' (using bytes for maximum speed)
                if b'/c/he/' in line:
                    continue
                
                try:
                    # Decode and parse tab-separated columns
                    decoded = line.decode('utf-8')
                    parts = decoded.strip().split('\t')
                    if len(parts) < 5:
                        continue
                    
                    relation = parts[1]
                    start = parts[2]
                    end = parts[3]
                    metadata_json = parts[4]
                    
                    # Parse weight from JSON metadata
                    try:
                        metadata = json.loads(metadata_json)
                        weight = float(metadata.get('weight', 1.0))
                    except Exception:
                        weight = 1.0
                        
                    batch.append((relation, start, end, weight))
                    inserted_count += 1
                    
                    if len(batch) >= batch_size:
                        cursor.executemany("""
                            INSERT INTO assertions (relation, start, end, weight)
                            VALUES (?, ?, ?, ?)
                        """, batch)
                        conn.commit()
                        batch = []
                        
                        elapsed = time.time() - start_time
                        rate = count / elapsed if elapsed > 0 else 0
                        print(f"Processed: {count:,} lines | Inserted: {inserted_count:,} | Elapsed: {elapsed:.1f}s | Speed: {rate:.0f} lines/s")
                        
                except Exception as parse_error:
                    # Silently skip malformed lines in a large dump
                    continue
                    
            # Insert remaining records in batch
            if batch:
                cursor.executemany("""
                    INSERT INTO assertions (relation, start, end, weight)
                    VALUES (?, ?, ?, ?)
                """, batch)
                conn.commit()
                
        elapsed = time.time() - start_time
        print(f"\nImport finished! Processed {count:,} lines, inserted {inserted_count:,} assertions in {elapsed:.2f} seconds.")
        
        # Build indexes for lightning-fast queries
        print("Building indexes on start and end columns...")
        idx_start_time = time.time()
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assertions_start ON assertions(start);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assertions_end ON assertions(end);")
        conn.commit()
        print(f"Indexes built successfully in {time.time() - idx_start_time:.2f} seconds.")
        
    except Exception as e:
        print(f"\nError during database import: {e}")
        conn.rollback()
        raise e
    finally:
        conn.close()

def main():
    start_total = time.time()
    
    # 1. Download
    try:
        download_file(CONCEPTNET_URL, DOWNLOAD_PATH)
    except Exception:
        print("Download failed. Aborting.")
        sys.exit(1)
        
    # 2. Import and Filter
    try:
        import_to_sqlite(DOWNLOAD_PATH, DB_PATH)
    except Exception:
        print("Import failed. Aborting.")
        sys.exit(1)
        
    # 3. Clean up the downloaded gzip file
    if os.path.exists(DOWNLOAD_PATH):
        print(f"Cleaning up: Removing downloaded file {DOWNLOAD_PATH}...")
        os.remove(DOWNLOAD_PATH)
        
    total_time = time.time() - start_total
    db_size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
    print("\n" + "="*50)
    print(f"ConceptNet offline import finished successfully!")
    print(f"Total time taken: {total_time/60:.2f} minutes")
    print(f"Offline DB Path: {DB_PATH}")
    print(f"Offline DB Size: {db_size_mb:.2f} MB")
    print("="*50)

if __name__ == "__main__":
    main()
