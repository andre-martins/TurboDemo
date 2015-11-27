#!/usr/bin/env python

import os
import sys

TURBO_PARSER_HOME = '/home/afm/projects/TurboParser'
TURBO_PARSER_PYTHON = os.sep.join([TURBO_PARSER_HOME, 'python'])
TURBO_PARSER_LIBS = os.sep.join([TURBO_PARSER_HOME,  'deps', 'local', 'lib'])

os.environ['LD_LIBRARY_PATH'] += ':' + TURBO_PARSER_LIBS
os.environ['LD_LIBRARY_PATH'] += ':' + TURBO_PARSER_PYTHON
os.environ['PYTHONPATH'] = ':' + TURBO_PARSER_PYTHON

#sys.path.append(TURBO_PARSER_PYTHON)

#sys.path.append(os.getcwd())
#sys.path.append(os.sep.join([TURBO_PARSER_HOME, 'deps', 'local', 'lib']))
#sys.path.append(os.sep.join([TURBO_PARSER_HOME, 'python']))

os.system('python turbo_demo.py')
