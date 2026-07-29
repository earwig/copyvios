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

CREATE TABLE history (
    hist_id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    hist_cache_id VARCHAR(32) NOT NULL,
    hist_site VARCHAR(1024) NOT NULL,
    hist_page_title VARCHAR(1024) NOT NULL,
    hist_query_oldid VARCHAR(16) DEFAULT NULL,
    hist_timestamp TIMESTAMP NOT NULL DEFAULT current_timestamp(),
    hist_user VARCHAR(1024) DEFAULT NULL,
    hist_best_url VARCHAR(1024) DEFAULT NULL,
    hist_best_confidence DOUBLE NOT NULL DEFAULT 0,
    hist_num_queries INT(4) NOT NULL DEFAULT 0,
    hist_process_time DOUBLE NOT NULL DEFAULT 0,
    hist_use_engine BOOLEAN NOT NULL DEFAULT 0,
    hist_use_links BOOLEAN NOT NULL DEFAULT 0,
    hist_did_short_circuit BOOLEAN NOT NULL DEFAULT 0,
    hist_via_api BOOLEAN NOT NULL DEFAULT 0,
    PRIMARY KEY (hist_id),
    KEY hist_timestamp_idx (hist_timestamp),
    KEY hist_page_idx (hist_site(64), hist_page_title(128)),
    KEY hist_user_idx (hist_user(128))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
