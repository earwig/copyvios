# -*- coding: utf-8  -*-

from re import sub, UNICODE

def highlight_delta(chain, delta):
    processed = []
    prev_prev = prev = chain.START
    i = 0
    all_words = chain.text.split()
    paragraphs = chain.text.split("\n")
    for paragraph in paragraphs:
        processed_words = []
        words = paragraph.split(" ")
        for i, word in enumerate(words, i):
            try:
                next = _strip_word(all_words[i+1])
            except IndexError:
                next = chain.END
            sword = _strip_word(word)
            block = (prev_prev, prev)  # Block for before
            alock = (prev, sword)  # Block for after
            before = [block in delta.chain and sword in delta.chain[block]]
            after = [alock in delta.chain and next in delta.chain[alock]]
            is_first = i == 0
            is_last = i + 1 == len(all_words)
            res = _highlight_word(word, before, after, is_first, is_last)
            processed_words.append(res)
            prev_prev = prev
            prev = sword
        processed.append(u" ".join(processed_words))
        i += 1
    return u"<br /><br />".join(processed)

def _highlight_word(word, before, after, is_first, is_last):
    if before and after:
        # Word is in the middle of a highlighted block, so don't change
        # anything unless this is the first word (force block to start) or
        # the last word (force block to end):
        res = word
        if is_first:
            res = u'<span class="cv-hl">' + res
        if is_last:
            res += u'</span>'
    elif before:
        # Word is the last in a highlighted block, so fade it out and then
        # end the block; force open a block before the word if this is the
        # first word:
        res = _fade_word(word, u"out") + u"</span>"
        if is_first:
            res = u'<span class="cv-hl">' + res
    elif after:
        # Word is the first in a highlighted block, so start the block and
        # then fade it in; force close the block after the word if this is
        # the last word:
        res = u'<span class="cv-hl">' + _fade_word(word, u"in")
        if is_last:
            res += u"</span>"
    else:
        # Word is completely outside of a highlighted block, so do nothing:
        res = word
    return res

def _fade_word(word, dir):
    if len(word) <= 4:
        return u'<span class="cv-hl-{0}">{1}</span>'.format(dir, word)
    if dir == u"out":
        return u'{0}<span class="cv-hl-out">{1}</span>'.format(word[:-4], word[-4:])
    return u'<span class="cv-hl-in">{0}</span>{1}'.format(word[:4], word[4:])

def _strip_word(word):
    return sub("[^\w\s-]", "", word.lower(), flags=UNICODE)
