import sys
import os
import re
from span import *
import nlp_utils
import pdb

def decorate_coref(coref_document):
    colornames = ['aqua', 'blue', 'fuchsia', 'green', 'lime', 'maroon',
                  'navy', 'olive', 'orange', 'purple', 'red', 'teal']

    decorated_coref_document = [] #''
    decorated_coref_sentence = []
    canonical_coref_ids = []
    words = []
    coref_info = []
    for line in coref_document.split('\n'):
        line = line.rstrip('\n')
        if line == '':
            spans = nlp_utils.construct_coreference_spans_from_text(coref_info)
            for i, word in enumerate(words):
                word_spans = []
                for span in spans:
                    if span.start <= i and span.end >= i:
                        word_spans.append(span)
                if len(word_spans) == 0:
                    color = 'black'
                else:
                    coref_id = int(word_spans[0].name)
                    if coref_id in canonical_coref_ids:
                        canonical_coref_id = canonical_coref_ids.index(coref_id)
                    else:
                        canonical_coref_id = len(canonical_coref_ids)
                        canonical_coref_ids.append(coref_id)
                    #canonical_coref_id = coref_id
                    id = canonical_coref_id % len(colornames)
                    color = colornames[id]
                span_names = '; '.join([span.name for span in word_spans])
                decorated_coref_sentence.append((word, span_names, color))
                #word_html = '<span title="%s"><font color="%s">%s</font></span>' % (span_names, color, word)
                #decorated_coref_document += word_html + ' '
            #decorated_coref_document += '<br/>\n'
            decorated_coref_document.append(decorated_coref_sentence)
            decorated_coref_sentence = []
            words = []
            coref_info = []
            continue
        if line.startswith('#begin document') or line.startswith('#end document'):
            decorated_coref_document += '<h1>%s</h1>\n' % line
            canonical_coref_ids = []
            continue
        fields = line.split('\t')
        word = fields[3]
        coref = fields[-1]
        words.append(word)
        coref_info.append(coref)
    
    return decorated_coref_document

