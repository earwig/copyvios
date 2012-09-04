# -*- coding: utf-8  -*-

from re import sub, UNICODE

from markupsafe import escape

def highlight_delta(context, chain, delta):
    processed = []
    dchain = delta.chain
    prev_prev = prev = chain.START
    i = 0
    all_words = chain.text.split()
    paragraphs = chain.text.split("\n")
    for paragraph in paragraphs:
        processed_words = []
        words = paragraph.split(" ")
        for i, word in enumerate(words, i):
            try:
                next = _strip_word(all_words[i + 1])
                try:
                    next_next = _strip_word(all_words[i + 2])
                except IndexError:
                    next_next = chain.END
            except IndexError:
                next = next_next = chain.END
            sword = _strip_word(word)
            middle = (prev, sword) in dchain and next in dchain[(prev, sword)]
            if middle:
                before = after = True
            else:
                b_block = (prev_prev, prev)
                a_block = (sword, next)
                before = b_block in dchain and sword in dchain[b_block]
                after = a_block in dchain and next_next in dchain[a_block]
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
        # anything unless this is the first word (force block to start) or the
        # last word (force block to end):
        res = unicode(escape(word))
        if is_first:
            res = u'<span class="cv-hl">' + res
        if is_last:
            res += u'</span>'
    elif before:
        # Word is the last in a highlighted block, so fade it out and then end
        # the block; force open a block before the word if this is the first
        # word:
        res = _fade_word(word, u"out") + u"</span>"
        if is_first:
            res = u'<span class="cv-hl">' + res
    elif after:
        # Word is the first in a highlighted block, so start the block and then
        # fade it in; force close the block after the word if this is the last
        # word:
        res = u'<span class="cv-hl">' + _fade_word(word, u"in")
        if is_last:
            res += u"</span>"
    else:
        # Word is completely outside of a highlighted block, so do nothing:
        res = unicode(escape(word))
    return res

def _fade_word(word, dir):
    if len(word) <= 4:
        word = unicode(escape(word))
        return u'<span class="cv-hl-{0}">{1}</span>'.format(dir, word)
    if dir == u"out":
        before, after = unicode(escape(word[:-4])), unicode(escape(word[-4:]))
        base = u'{0}<span class="cv-hl-out">{1}</span>'
        return base.format(before, after)
    else:
        before, after = unicode(escape(word[:4])), unicode(escape(word[4:]))
        base = u'<span class="cv-hl-in">{0}</span>{1}'
        return base.format(before, after)

def _strip_word(word):
    return sub("[^\w\s-]", "", word.lower(), flags=UNICODE)
