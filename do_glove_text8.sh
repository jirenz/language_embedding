
export DATA_PATH=/datadrive/data
export SIGNAL_FILE=.created_at.txt

ARTICLE_PATH=$DATA_PATH/text8
OUTPUT_PATH=$DATA_PATH/glove_text8_debug
COOC_FILE=$OUTPUT_PATH/text8.cooc
COOCCURRENCE_SHUF_FILE=$OUTPUT_PATH/cooc.shuff.bin
VOCAB_FILE=$OUTPUT_PATH/vocab.txt

NUM_WORKERS=1
NUM_THREADS=6

X_MAX=50
ALPHA=0.75
ETA=0.05
SAVE_PER=5

MAX_ITER=25
VECTOR_SIZE=50
BINARY=2
VERBOSE=2

MEMORY=40

SAVE_FILE=$OUTPUT_PATH/vectors

BUILDDIR=glove/build/

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

if [ ! -e $COOC_FILE ]; then
	echo "$ python count_cooc_signals.py -o $OUTPUT_PATH $ARTICLE_PATH"
	python count_cooc_signals.py -o $OUTPUT_PATH $ARTICLE_PATH
	if [ $? -eq 0 ]; then
		echo successfully counted cooccurrence
	else
		exit -1
	fi
fi

if [ ! -e $COOCCURRENCE_SHUF_FILE ]; then
	echo "$ $BUILDDIR/shuffle -memory $MEMORY -verbose $VERBOSE < $COOC_FILE > $COOCCURRENCE_SHUF_FILE"
	$BUILDDIR/shuffle -memory $MEMORY -verbose $VERBOSE < $COOC_FILE > $COOCCURRENCE_SHUF_FILE
	if [ $? -eq 0 ]; then
		echo successfully shuffled cooccurrence
	else
		exit -1
	fi
fi


echo "$ $BUILDDIR/glove -save-file $SAVE_FILE -threads $NUM_THREADS -input-file
 $COOCCURRENCE_SHUF_FILE -x-max $X_MAX -iter $MAX_ITER -vector-size $VECTOR_SIZE -binary $BINARY -vocab-file $VOCAB_FILE -verbose $VERBOSE -alpha $ALPHA -checkpoint-every $SAVE_PER"
$BUILDDIR/glove -save-file $SAVE_FILE -threads $NUM_THREADS -input-file $COOCCURRENCE_SHUF_FILE \
                -x-max $X_MAX -iter $MAX_ITER -vector-size $VECTOR_SIZE -binary $BINARY\
                -vocab-file $VOCAB_FILE -verbose $VERBOSE -alpha $ALPHA -checkpoint-every $SAVE_PER