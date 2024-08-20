MAKEJS  := uglifyjs --compress
MAKECSS := postcss -u cssnano --no-map

.PHONY: all

.INTERMEDIATE: static/style.tmp.css

all: js css

js: static/script.min.js

css: static/style.min.css static/api.min.css

static/script.min.js: static/script.js
	$(MAKEJS) -o $@ -- $^

static/style.tmp.css: static/css/*.css
	cat $^ > $@

static/style.min.css: static/style.tmp.css
	$(MAKECSS) -o $@ $^

static/api.min.css: static/api.css
	$(MAKECSS) -o $@ $^
