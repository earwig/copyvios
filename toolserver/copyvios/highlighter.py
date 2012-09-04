# -*- coding: utf-8  -*-

from re import sub, UNICODE

from markupsafe import escape

def highlight_delta(context, chain, delta):
    degree = chain.degree - 1
    highlights = [False] * degree
    block = [chain.START] * degree
    for word in chain.text.split() + ([chain.END] * degree):
        word = _strip_word(chain, word)
        tblock = tuple(block)
        if tblock in delta.chain and word in delta.chain[tblock]:
            highlights[-1 * degree:] = [True] * degree
            highlights.append(True)
        else:
            highlights.append(False)
        block.pop(0)
        block.append(word)

    i = degree
    numwords = len(chain.text.split())
    processed = []
    for paragraph in chain.text.split("\n"):
        words = []
        for i, word in enumerate(paragraph.split(), i):
            before = highlights[i - 1]
            after = highlights[i + 1]
            first = i == degree
            last = i - degree + 1 == numwords
            words.append(_highlight_word(word, before, after, first, last))
        processed.append(u" ".join(words))
        i += 1

    return u"<p>" + u"</p>\n<p>".join(processed) + u"</p>"

def _highlight_word(word, before, after, first, last):
    if before and after:
        # Word is in the middle of a highlighted block, so don't change
        # anything unless this is the first word (force block to start) or the
        # last word (force block to end):
        res = unicode(escape(word))
        if first:
            res = u'<span class="cv-hl">' + res
        if last:
            res += u'</span>'
    elif before:
        # Word is the last in a highlighted block, so fade it out and then end
        # the block; force open a block before the word if this is the first
        # word:
        res = _fade_word(word, u"out") + u"</span>"
        if first:
            res = u'<span class="cv-hl">' + res
    elif after:
        # Word is the first in a highlighted block, so start the block and then
        # fade it in; force close the block after the word if this is the last
        # word:
        res = u'<span class="cv-hl">' + _fade_word(word, u"in")
        if last:
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

def _strip_word(chain, word):
    if word == chain.START or word == chain.END:
        return word
    return sub("[^\w\s-]", "", word.lower(), flags=UNICODE)
