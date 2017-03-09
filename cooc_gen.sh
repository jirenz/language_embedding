#!/bin/bash
#
#
export DATA_PATH=/datadrive/data
export SIGNAL_FILE=.created_at.txt

ARTICLE_PATH=$DATA_PATH/wiki_articles/AA
COOC_PATH=$DATA_PATH/enriched_cooc
OUTPUT_PATH=$DATA_PATH/enriched_glove
COOCCURRENCE_SHUF_FILE=$OUTPUT_PATH/cooc.suff.bin
VOCAB_FILE=$OUTPUT_PATH/vocab.txt

NUM_WORKERS=3
NUM_THREADS=6

X_MAX=100
ALPHA=0.75
ETA=0.05
SAVE_PER=5

MAX_ITER=25
VECTOR_SIZE=100
BINARY=2
VERBOSE=2

if [ ! -e $VOCAB_FILE ]; then
	echo "$ mkdir -pv $OUTPUT_PATH"
	mkdir -pv $OUTPUT_PATH
	echo "$ python generate_vocab.py $VOCAB_FILE"
	python generate_vocab.py $VOCAB_FILE
	if [ $? -eq 0 ]; then
		echo successfully generated vocabulary
	else
		exit -1
	fi
fi

if [ ! -e $COOC_PATH/$SIGNAL_FILE ]; then
	echo "$ mkdir -pv $COOC_PATH"
	mkdir -pv $COOC_PATH
	echo "$ find $ARTICLE_PATH/wiki_0* 2>>log.txt | xargs python chunked_cooc.py -o $COOC_PATH --cores $NUM_WORKERS"
	# find $ARTICLE_PATH/wiki_0* 2>>log.txt | xargs python chunked_cooc.py -o $COOC_PATH --cores $NUM_WORKERS
	python chunked_cooc.py -o $COOC_PATH --cores $NUM_WORKERS $ARTICLE_PATH/wiki_00 $ARTICLE_PATH/wiki_01 $ARTICLE_PATH/wiki_02
	if [ $? -eq 0 ]; then
		echo successfully counted cooccurrence by chunk
	else
		exit -1
	fi
fi

if [ ! -e $COOCCURRENCE_SHUF_FILE ]; then
	echo "$ mkdir -pv $OUTPUT_PATH"
	mkdir -pv $OUTPUT_PATH
	echo "$ find $COOC_PATH/wiki_0* 2>>log.txt | xargs python cooc_reduce.py -o $COOCCURRENCE_SHUF_FILE"
	# find $COOC_PATH/wiki_0* 2>>log.txt | xargs python cooc_reduce.py -o $COOCCURRENCE_SHUF_FILE
	find $COOC_PATH/wiki_0* 2>>log.txt | xargs python cooc_reduce.py -o $COOCCURRENCE_SHUF_FILE
	if [ $? -eq 0 ]; then
		echo successfully collected cooccurrence
	else
		exit -1
	fi
fi


echo "$ $BUILDDIR/glove -save-file $SAVE_FILE -threads $NUM_THREADS -input-file
 $COOCCURRENCE_SHUF_FILE -x-max $X_MAX -iter $MAX_ITER -vector-size $VECTOR_SIZE -binary $BINARY -vocab-file $VOCAB_FILE -verbose $VERBOSE -alpha $ALPHA -checkpoint-every $SAVE_PER"
$BUILDDIR/glove -save-file $SAVE_FILE -threads $NUM_THREADS -input-file $COOCCURRENCE_SHUF_FILE \
                -x-max $X_MAX -iter $MAX_ITER -vector-size $VECTOR_SIZE -binary $BINARY\
                -vocab-file $VOCAB_FILE -verbose $VERBOSE -alpha $ALPHA -checkpoint-every $SAVE_PER
