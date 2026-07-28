CREATE TABLE cache (
    cache_id VARCHAR(32) NOT NULL,
    cache_site VARCHAR(1024) NOT NULL,
    cache_page_title VARCHAR(1024) NOT NULL,
    cache_time TIMESTAMP NOT NULL DEFAULT current_timestamp(),
    cache_user VARCHAR(1024) DEFAULT NULL,
    cache_queries INT(4) NOT NULL DEFAULT 0,
    cache_process_time DOUBLE NOT NULL DEFAULT 0,
    cache_possible_miss BOOLEAN NOT NULL DEFAULT 0,
    PRIMARY KEY (cache_id),
    KEY cache_time_idx (cache_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;

CREATE TABLE cache_data (
    cdata_id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    cdata_cache_id VARCHAR(32) NOT NULL,
    cdata_url VARCHAR(1024) NOT NULL,
    cdata_confidence DOUBLE NOT NULL DEFAULT 0,
    cdata_skipped BOOLEAN NOT NULL DEFAULT 0,
    cdata_excluded BOOLEAN NOT NULL DEFAULT 0,
    PRIMARY KEY (cdata_id),
    KEY cdata_cache_id (cdata_cache_id),
    FOREIGN KEY (cdata_cache_id) REFERENCES cache (cache_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
