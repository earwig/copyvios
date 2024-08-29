from collections import deque
from re import UNICODE, sub

from earwigbot.wiki.copyvios.markov import EMPTY_INTERSECTION
from markupsafe import escape

__all__ = ["highlight_delta"]


def highlight_delta(context, chain, delta):
    degree = chain.degree - 1
    highlights = [False] * degree
    block = deque([chain.START] * degree)
    if not delta:
        delta = EMPTY_INTERSECTION
    for word in chain.text.split() + ([chain.END] * degree):
        word = _strip_word(chain, word)
        block.append(word)
        if tuple(block) in delta.chain:
            highlights[-1 * degree :] = [True] * degree
            highlights.append(True)
        else:
            highlights.append(False)
        block.popleft()

    i = degree
    numwords = len(chain.text.split())
    result = []
    paragraphs = deque(chain.text.split("\n"))
    while paragraphs:
        words = []
        for i, word in enumerate(_get_next(paragraphs), i):
            if highlights[i]:
                before = highlights[i - 1]
                after = highlights[i + 1]
                first = i == degree
                last = i - degree + 1 == numwords
                words.append(_highlight_word(word, before, after, first, last))
            else:
                words.append(str(escape(word)))
        result.append(" ".join(words))
        i += 1

    return "<br /><br />".join(result)


def _get_next(paragraphs):
    body = []
    while paragraphs and not body:
        body = paragraphs.popleft().split()
    if body and len(body) <= 3:
        while paragraphs:
            next = paragraphs[0].split()
            if len(next) <= 3:
                body += next
                paragraphs.popleft()
            else:
                break
    return body


def _highlight_word(word, before, after, first, last):
    if before and after:
        # Word is in the middle of a highlighted block:
        res = str(escape(word))
        if first:
            res = '<span class="cv-hl">' + res
        if last:
            res += "</span>"
    elif after:
        # Word is the first in a highlighted block:
        res = '<span class="cv-hl">' + _fade_word(word, "in")
        if last:
            res += "</span>"
    elif before:
        # Word is the last in a highlighted block:
        res = _fade_word(word, "out") + "</span>"
        if first:
            res = '<span class="cv-hl">' + res
    else:
        res = str(escape(word))
    return res


def _fade_word(word, dir):
    if len(word) <= 4:
        word = str(escape(word))
        return f'<span class="cv-hl-{dir}">{word}</span>'
    if dir == "out":
        before, after = str(escape(word[:-4])), str(escape(word[-4:]))
        base = '{0}<span class="cv-hl-out">{1}</span>'
        return base.format(before, after)
    else:
        before, after = str(escape(word[:4])), str(escape(word[4:]))
        base = '<span class="cv-hl-in">{0}</span>{1}'
        return base.format(before, after)


def _strip_word(chain, word):
    if word == chain.START or word == chain.END:
        return word
    return sub("[^\w\s-]", "", word.lower(), flags=UNICODE)
