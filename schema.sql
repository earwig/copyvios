CREATE TABLE cache (
    cache_id BINARY(32) NOT NULL,
    cache_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cache_queries INT(4) NOT NULL DEFAULT 0,
    cache_process_time DOUBLE NOT NULL DEFAULT 0,
    cache_possible_miss BOOLEAN NOT NULL DEFAULT 0,
    PRIMARY KEY (cache_id)
);
CREATE INDEX cache_time_idx ON cache (cache_time);
CREATE TABLE cache_data (
    cdata_id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    cdata_cache_id BINARY(32) NOT NULL,
    cdata_url VARCHAR(1024) NOT NULL,
    cdata_confidence DOUBLE NOT NULL DEFAULT 0,
    cdata_skipped BOOLEAN NOT NULL DEFAULT 0,
    cdata_excluded BOOLEAN NOT NULL DEFAULT 0,
    PRIMARY KEY (cdata_id),
    FOREIGN KEY (cdata_cache_id) REFERENCES cache (cache_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);
