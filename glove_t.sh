#!/bin/bash
set -e
make glove
# Makes programs, downloads sample data, trains a GloVe model, and then evaluates it.
# One optional argument can specify the language used for eval script: matlab, octave or [default] python

# Version that operates on singly tokenized file
DATA_PATH=/datadrive/data
TOKENIZED_PATH=wiki_tokenized
GLOVE_PATH=glove

CORPUS=$DATA_PATH/$TOKENIZED_PATH/wiki_token
VOCAB_FILE=$GLOVE_PATH/vocab.txt
COOCCURRENCE_FILE=$GLOVE_PATH/cooccurrence.bin
COOCCURRENCE_SHUF_FILE=$GLOVE_PATH/cooccurrence.shuf.bin
BUILDDIR=$GLOVE_PATH/build
SAVE_FILE=$GLOVE_PATH/vectors
VERBOSE=2
MEMORY=40.0
VOCAB_MIN_COUNT=5
VECTOR_SIZE=100
MAX_ITER=15
WINDOW_SIZE=15
BINARY=2
NUM_THREADS=6
X_MAX=100

echo "$ $BUILDDIR/vocab_count -min-count $VOCAB_MIN_COUNT -verbose $VERBOSE < $CORPUS > $VOCAB_FILE"
$BUILDDIR/vocab_count -min-count $VOCAB_MIN_COUNT -verbose $VERBOSE < $CORPUS > $VOCAB_FILE
echo "$ $BUILDDIR/cooccur -memory $MEMORY -vocab-file $VOCAB_FILE -verbose $VERBOSE -window-size $WINDOW_SIZE < $CORPUS > $COOCCURRENCE_FILE"
$BUILDDIR/cooccur -memory $MEMORY -vocab-file $VOCAB_FILE -verbose $VERBOSE -window-size $WINDOW_SIZE < $CORPUS > $COOCCURRENCE_FILE
echo "$ $BUILDDIR/shuffle -memory $MEMORY -verbose $VERBOSE < $COOCCURRENCE_FILE > $COOCCURRENCE_SHUF_FILE"
$BUILDDIR/shuffle -memory $MEMORY -verbose $VERBOSE < $COOCCURRENCE_FILE > $COOCCURRENCE_SHUF_FILE
echo "$ $BUILDDIR/glove -save-file $SAVE_FILE -threads $NUM_THREADS -input-file $COOCCURRENCE_SHUF_FILE -x-max $X_MAX -iter $MAX_ITER -vector-size $VECTOR_SIZE -binary $BINARY -vocab-file $VOCAB_FILE -verbose $VERBOSE"
$BUILDDIR/glove -save-file $SAVE_FILE -threads $NUM_THREADS -input-file $COOCCURRENCE_SHUF_FILE -x-max $X_MAX -iter $MAX_ITER -vector-size $VECTOR_SIZE -binary $BINARY -vocab-file $VOCAB_FILE -verbose $VERBOSE
