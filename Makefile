MAKEJS  := uglifyjs --compress
MAKECSS := postcss -u cssnano --no-map

STATIC_DIR := src/copyvios/static

.PHONY: all js css

.INTERMEDIATE: $(STATIC_DIR)/style.tmp.css

all: js css

js: $(STATIC_DIR)/script.min.js

css: $(STATIC_DIR)/style.min.css $(STATIC_DIR)/api.min.css

$(STATIC_DIR)/script.min.js: $(STATIC_DIR)/script.js
	$(MAKEJS) -o $@ -- $^

$(STATIC_DIR)/style.tmp.css: $(STATIC_DIR)/css/*.css
	cat $^ > $@

$(STATIC_DIR)/style.min.css: $(STATIC_DIR)/style.tmp.css
	$(MAKECSS) -o $@ $^

$(STATIC_DIR)/api.min.css: $(STATIC_DIR)/api.css
	$(MAKECSS) -o $@ $^
