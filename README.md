# TurboDemo
A simple webapp in Flask that serves as a demo for [TurboParser](https://github.com/andre-martins/TurboParser).

## Installation instructions
1. Download and install TurboParser (see link above).
2. Install the Python wrapper for TurboParser (see link above).
3. Install flask (see http://flask.pocoo.org/).
4. Run the following commands, where <TurboParser> is the folder where TurboParser is installed:
```
git clone https://github.com/andre-martins/TurboDemo.git
cd TurboDemo
ln -s <TurboParser>/python/tokenizers tokenizers
ln -s <TurboParser>/python/lemmatizer.py lemmatizer.py
ln -s <TurboParser>/python/nlp_pipeline.py nlp_pipeline.py
ln -s <TurboParser>/python/nlp_pipeline.config nlp_pipeline.config
ln -s <TurboParser>/python/turboparser.so turboparser.so
ln -s <TurboParser>/python/libturboparser.so libturboparser.so
```

## Usage
1. Add the following to the library path:
```
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:<TurboParser>/deps/local/lib:"
```
2. Run the server:
```
cd TurboDemo
python turbo_demo.py
```
3. Point your browser to http://localhost:5000/turbo_demo.
4. Have fun!

## Licence
LGPL.
