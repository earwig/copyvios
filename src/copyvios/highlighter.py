__all__ = ["highlight_delta"]

import re
from collections import deque
from typing import Literal

import markupsafe
from earwigbot.wiki.copyvios.markov import (
    EMPTY_INTERSECTION,
    MarkovChain,
    MarkovChainIntersection,
    Sentinel,
)


def highlight_delta(chain: MarkovChain, delta: MarkovChainIntersection | None) -> str:
    degree = chain.degree - 1
    highlights = [False] * degree
    block: deque[str | Sentinel] = deque([Sentinel.START] * degree)
    if not delta:
        delta = EMPTY_INTERSECTION
    for word in chain.text.split() + ([Sentinel.END] * degree):
        word = _strip_word(word)
        block.append(word)
        if tuple(block) in delta.chain:
            highlights[-1 * degree :] = [True] * degree
            highlights.append(True)
        else:
            highlights.append(False)
        block.popleft()

    i = degree
    numwords = len(chain.text.split())
    result: list[str] = []
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
                words.append(str(markupsafe.escape(word)))
        result.append(" ".join(words))
        i += 1

    return "<br /><br />".join(result)


def _get_next(paragraphs: deque[str]) -> list[str]:
    body: list[str] = []
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


def _highlight_word(
    word: str, before: bool, after: bool, first: bool, last: bool
) -> str:
    if before and after:
        # Word is in the middle of a highlighted block
        res = str(markupsafe.escape(word))
        if first:
            res = '<span class="cv-hl">' + res
        if last:
            res += "</span>"
    elif after:
        # Word is the first in a highlighted block
        res = '<span class="cv-hl">' + _fade_word(word, "in")
        if last:
            res += "</span>"
    elif before:
        # Word is the last in a highlighted block
        res = _fade_word(word, "out") + "</span>"
        if first:
            res = '<span class="cv-hl">' + res
    else:
        res = str(markupsafe.escape(word))
    return res


def _fade_word(word: str, dir: Literal["in", "out"]) -> str:
    if len(word) <= 4:
        word = str(markupsafe.escape(word))
        return f'<span class="cv-hl-{dir}">{word}</span>'
    if dir == "out":
        before = str(markupsafe.escape(word[:-4]))
        after = str(markupsafe.escape(word[-4:]))
        return f'{before}<span class="cv-hl-out">{after}</span>'
    else:
        before = str(markupsafe.escape(word[:4]))
        after = str(markupsafe.escape(word[4:]))
        return f'<span class="cv-hl-in">{before}</span>{after}'


def _strip_word(word: str | Sentinel) -> str | Sentinel:
    if word == Sentinel.START or word == Sentinel.END:
        return word
    return re.sub(r"[^\w\s-]", "", word.lower())
