CREATE TABLE cache (
    cache_id BLOB NOT NULL,
    cache_time INTEGER NOT NULL DEFAULT (STRFTIME('%s', 'now')),
    cache_queries INTEGER NOT NULL DEFAULT 0,
    cache_process_time REAL NOT NULL DEFAULT 0,
    cache_possible_miss INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (cache_id)
);
CREATE INDEX cache_time_idx ON cache (cache_time);
CREATE TABLE cache_data (
    cdata_id ROWID,
    cdata_cache_id BLOB NOT NULL,
    cdata_url TEXT NOT NULL,
    cdata_confidence REAL NOT NULL DEFAULT 0,
    cdata_skipped INTEGER NOT NULL DEFAULT 0,
    cdata_excluded INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (cdata_id),
    FOREIGN KEY (cdata_cache_id) REFERENCES cache (cache_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);
