from flask import Flask, request, render_template
from flask.ext.wtf import Form
from wtforms import Form, BooleanField, TextField, TextAreaField, PasswordField, RadioField, SelectField, validators

import os
import sys
sys.path.append(os.getcwd())

import nlp_pipeline
pipeline = nlp_pipeline.NLPPipeline()

import threading
#import time

import json

app = Flask(__name__)

lock = threading.Lock()

class TurboDemoForm(Form):
    sentence = TextAreaField('Write the sentence here:',
                             [validators.Length(min=1, max=100000)])
    language = SelectField('Language:',
                           choices=[('PT', 'Portuguese'),
                                    ('ES', 'Spanish'),
                                    #('EN', 'English'),
                                    ('EN-Nonprojective', 'English-Nonprojective'),
                                    ('PT-BR-Universal', 'Brazilian Portuguese-Universal'),
                                    ('ES-Universal', 'Spanish-Universal'),
                                    ('FR-Universal', 'French-Universal'),
                                    ('IT-Universal', 'Italian-Universal'),
                                    ('DE-Universal', 'German-Universal')])
    entity_tagged_sentence = ''
    parsed_sentence = ''
    parsed_sentence_json = '{}'
    semantic_parsed_sentence = ''
    semantic_parsed_sentence_json = '{}'
    coref_document = ''
    decorated_coref_document = ''
    coref_document_json = '{}'

@app.route('/turbo_demo', methods=['GET', 'POST'])
def turbo_demo():
    form = TurboDemoForm(request.form)
    if request.method == 'POST' and form.validate():
        text = form.sentence.data.encode('utf-8')
        language = form.language.data
        print "Lock acquire"
        lock.acquire()
        sentences = pipeline.split_sentences(text, language)

        entity_tagged_sentence = ''
        parsed_sentence = ''
        semantic_parsed_sentence = ''
        coref_document = ''
        decorated_coref_document = ''
        
        if 'parse' in request.form:
            # Only process the first sentence.
            sentence = sentences[0]
            #parsed_sentence = pipeline.parse_conll(sentence, language)

            tokenized_sentence = pipeline.tokenize(sentence, language)
            tags, lemmas = pipeline.tag(tokenized_sentence, language)

            if pipeline.has_entity_recognizer(language):
                entity_tags = pipeline.recognize_entities(tokenized_sentence,
                                                      tags, language)
                entity_tagged_sentence = ''
                prefixes = [tag[:1] for tag in entity_tags]
                entities = [tag[2:] for tag in entity_tags]
                for i, token in enumerate(tokenized_sentence):
                    if prefixes[i] == 'B':
                        entity_tagged_sentence += '[' + entities[i] + ' '
                    entity_tagged_sentence += token + ' '
                    if prefixes[i] != 'O' and \
                            (i == len(tokenized_sentence)-1 or prefixes[i+1] != 'I'):
                        entity_tagged_sentence += '] '
                print entity_tagged_sentence
            else:
                entity_tagged_sentence = ''

            heads, deprels = pipeline.parse(tokenized_sentence, tags, lemmas, language)
            parsed_sentence = ''
            for i, token in enumerate(tokenized_sentence):
                parsed_sentence += str(i+1) + '\t' + token + '\t' + lemmas[i] + \
                    '\t' + tags[i] + '\t' + tags[i] + '\t_\t' + str(heads[i]) + \
                    '\t' + deprels[i] + '\n'
            parsed_sentence += '\n'

            if pipeline.has_semantic_parser(language):
                predicates, argument_lists = \
                    pipeline.parse_semantic_dependencies(tokenized_sentence, tags,
                                                         lemmas, heads, deprels,
                                                         language)
                semantic_parsed_sentence = ''
                for i, token in enumerate(tokenized_sentence):
                    semantic_output = predicates[i] + '\t' + '\t'.join(argument_lists[i])
                    #if len(argument_lists[i]) > 0:
                    #    semantic_output += '\t' + '\t'.join(argument_lists[i])
                    semantic_parsed_sentence += str(i+1) + '\t_\t_\t_\t_\t' + token \
                        + '\t' + lemmas[i] + '\t' + tags[i] + '\t' + str(heads[i]) \
                        + '\t' + deprels[i] + '\t' + semantic_output + '\n'
                semantic_parsed_sentence += '\n'
            else:
                semantic_parsed_sentence = ''

        elif 'resolve_coreferences' in request.form:

            all_tokenized_sentences = []
            all_tags = []
            all_lemmas = []
            all_heads = []
            all_deprels = []
            all_entity_tags = []

            # Process all sentences.
            for sentence in sentences:
                tokenized_sentence = pipeline.tokenize(sentence, language)
                tags, lemmas = pipeline.tag(tokenized_sentence, language)
                heads, deprels = pipeline.parse(tokenized_sentence, tags, lemmas, language)
                # TODO(atm): replace this by actual entity tags.
                entity_tags = ['*' for i in xrange(len(tags))]
                all_tokenized_sentences.append(tokenized_sentence)
                all_tags.append(tags)
                all_lemmas.append(lemmas)
                all_heads.append(heads)
                all_deprels.append(deprels)
                all_entity_tags.append(entity_tags)

            all_coref_info = pipeline.resolve_coreferences(all_tokenized_sentences,
                                                           all_tags,
                                                           all_lemmas,
                                                           all_heads,
                                                           all_deprels,
                                                           all_entity_tags,
                                                           language)
            coref_document = ''
            for j, tokenized_sentence in enumerate(all_tokenized_sentences):
                tags = all_tags[j]
                lemmas = all_lemmas[j]
                heads = all_heads[j]
                deprels = all_deprels[j]
                entity_tags = all_entity_tags[j]
                coref_info = all_coref_info[j]
                for i, token in enumerate(tokenized_sentence):
                    tag = tags[i]
                    lemma = lemmas[i]
                    head = heads[i]
                    deprel = deprels[i]
                    entity_tag = entity_tags[i]
                    coref = coref_info[i]
                    coref_document += '\t'.join(['_', '0', str(i+1), token, tag,
                                                 '*', str(head), deprel,
                                                 '-', '-', '-', '-', entity_tag,
                                                 coref])
                    coref_document += '\n'
                coref_document += '\n'
            #print coref_document

        else:
            assert False

        #time.sleep(5)
        print "Lock release"
        lock.release()
        form.entity_tagged_sentence = entity_tagged_sentence.decode('utf-8')
        form.parsed_sentence = parsed_sentence.decode('utf-8')
        form.semantic_parsed_sentence = semantic_parsed_sentence.decode('utf-8')
        form.coref_document = coref_document.decode('utf-8')
        import conll_to_json as ctj
        lines = form.parsed_sentence.split('\n')
        conll_string = ''
        for line in lines:
            line = line.rstrip('\n')
            if line == '':
                conll_string += '\n'
            else:
                conll_string += line + '\t_\t_\n'
        json_string = ctj.encode_conll(conll_string)
        form.parsed_sentence_json = json.dumps(json_string)
        print form.parsed_sentence_json

        lines = form.semantic_parsed_sentence.split('\n')
        conll2008_string = ''
        for line in lines:
            line = line.rstrip('\n')
            if line == '':
                conll2008_string += '\n'
            else:
                conll2008_string += line + '\n'
        json_string = ctj.encode_conll2008(conll2008_string)
        form.semantic_parsed_sentence_json = json.dumps(json_string)
        print form.semantic_parsed_sentence_json

        import pdb
        import decorate_coref as dc
        #pdb.set_trace()
        decorated_coref_document = dc.decorate_coref(form.coref_document)
        #print decorated_coref_document
        form.decorated_coref_document = decorated_coref_document
        

    return render_template('turbo_demo.html', form=form)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
    #app.run(host='0.0.0.0')
