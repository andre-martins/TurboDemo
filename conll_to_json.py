"""
Converts a dependency parse in conll format into json suitable for visualizing
with brat (brat.nlplab.org).

Author: Lingpeng Kong, Sam Thomson
"""
from pos_to_conll import ConllToken
import re
import pdb

def get_char_offsets(words):
    """ Calculates character offsets of tokens """
    start = 0
    offsets = []
    for word in words:
        end = start + len(word)
        offsets.append([start, end])
        start = end + 1
    return offsets


def encode_conll(conll_data):
    """
    Converts a dependency parse in conll format into json suitable for
    visualizing with brat (brat.nlplab.org).
    """
    rows = [row.split('\t')
            for row in conll_data.splitlines() if row.strip()]
    tokens = [ConllToken(*row) for row in rows]
    words = [token.form for token in tokens]
    text = ' '.join(words)

    # tokens
    entities = [["T%s" % token.id, token.postag, [offset]]
                for token, offset in zip(tokens, get_char_offsets(words))]

    # dependency arcs
    non_roots = [token for token in tokens if int(token.head) != 0]
    relations = [['R%s' % (i + 1),
                  tok.deprel,
                  [['Arg1', 'T' + tok.head],
                   ['Arg2', 'T' + tok.id]]]
                 for i, tok in enumerate(non_roots)]

    return {
        "text": text,
        "entities": entities,
        "relations": relations
    }


def encode_conll2008(conll_data):
    """
    Converts a semantic parse in conll 2008 format into json suitable for
    visualizing with brat (brat.nlplab.org).
    """
    rows = [row.rstrip('\t').split('\t')
            for row in conll_data.splitlines() if row.strip()]
    words = [row[5] for row in rows]
    lemmas = [row[6] for row in rows]
    tags = [row[7] for row in rows]
    heads = [row[8] for row in rows]
    deprels = [row[9] for row in rows]
    predicates = [row[10] for row in rows]
    argument_list = [row[11:] for row in rows]

    text = ' '.join(words) #

    # tokens
    index_predicates = [(i, predicate) for (i, predicate) in enumerate(predicates) if predicate != '_']
    entities = [["T%s" % str(i+1), ('', predicate)[predicate != '_'], [offset]]
                for i, (predicate, offset) in enumerate(zip(predicates, get_char_offsets(words)))]

    # predicate-argument arcs
    arcs = []
    if len(words) > 0:
        assert len(index_predicates) == len(argument_list[0]), pdb.set_trace()
    #pdb.set_trace()
    for k, (p, predicate) in enumerate(index_predicates):
        predicate_arcs = [(p, a, roles[k]) for (a, roles) in enumerate(argument_list) if roles[k] != '_']
        arcs.extend(predicate_arcs)

    relations = [['R%s' % (i+1),
                  role,
                  [['Arg1', 'T' + str(p+1)],
                   ['Arg2', 'T' + str(a+1)]]]
                 for i, (p, a, role) in enumerate(arcs)]

    return {
        "text": text,
        "entities": entities,
        "relations": relations
    }
