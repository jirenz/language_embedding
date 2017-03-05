#!/bin/bash
# usage evaluate.sh [vector_file]

DATA_PATH=/datadrive/data
TOKENIZED_PATH=$DATA_PATH/wiki_tokenized
VECTOR_PATH=$DATA_PATH/vector/$1
LABEL_GRAM_PATH=$TOKENIZED_PATH/label_gram
GRAM_LABEL_PATH=$TOKENIZED_PATH/gram_label

python evaluate.py $VECTOR_PATH $LABEL_GRAM_PATH $GRAM_LABEL_PATH

echo Finished Evaluating Vectors