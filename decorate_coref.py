import sys
import os
import re
from span import *
import pdb

def construct_coreference_spans_from_text(span_lines):
    left_bracket = '('
    right_bracket = ')'
    characters_to_ignore = '*-'
    name = ''
    span_names_stack = []
    span_start_stack = []
    spans = []

    for i in xrange(len(span_lines)):
        line = span_lines[i]
        fields = line.split('|')
        for field in fields:
            if field[0] == left_bracket and field[-1] == right_bracket:
                start_position = i
                end_position = i
                name = field[1:-1]
                span = Span(start_position, end_position, name)
                spans.append(span)
            elif field[0] == left_bracket:
                start_position = i
                end_position = -1
                name = field[1:]
                span = Span(start_position, end_position, name)
                spans.append(span)
            elif field[-1] == right_bracket:
                name = field[:-1]
                selected_span = None
                for span in reversed(spans):
                    if span.name == name and span.end == -1:
                        assert selected_span == None, pdb.set_trace()
                        selected_span = span
                        break
                assert selected_span != None, pdb.set_trace()
                selected_span.end = i

    for span in spans:
        assert span.end != -1

    return spans


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
            spans = construct_coreference_spans_from_text(coref_info)
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

