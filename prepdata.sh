#!/bin/bash
DATA_PATH=/datadrive/data

RAW_DATA_FILE=enwiki-20170220-pages-articles-multistream.xml.bz2
RAW_DATA_URL=https://dumps.wikimedia.org/enwiki/20170220/enwiki-20170220-pages-articles-multistream.xml.bz2

UNZIPPED_DATA_FILE=enwiki-20170220-pages-articles-multistream.xml

WIKI_EXTRACT_PATH=WikiDump
CHUNK_SIZE=150M
CHUNKED_ARTICLES_PATH=wiki_articles

GRAM_W_COUNT_PATH=wiki_gram
GRAM_W_COUNT_SIZE=3

GRAM_TRIM_PATH=wiki_gram_trimmed
GRAM_TRIM_THRESHOLD=2

GRAM_COLLECT_PATH=wiki_gram_collected
GRAM_COLLECT_FILE_NAME=wiki_grams
GRAM_COLLECT_FILE=$DATA_PATH/$GRAM_COLLECT_PATH/$GRAM_COLLECT_FILE_NAME

TOKENIZED_PATH=wiki_tokenized

PROCESSED_DUMP_NAME=wiki_token

SIGNAL_FILE=.created_at.txt

rm log.txt

#Download files
if [ ! -e $DATA_PATH/$RAW_DATA_FILE ]; then
	wget $RAW_DATA_URL -O $DATA_PATH/$RAW_DATA_FILE
fi
if [ ! -e $DATA_PATH/$UNZIPPED_DATA_FILE ]; then
	bzip2 -dc $DATA_PATH/$RAW_DATA_FILE > $DATA_PATH/$UNZIPPED_DATA_FILE
fi
#Chunk data
if [ ! -e $DATA_PATH/$CHUNKED_ARTICLES_PATH/$SIGNAL_FILE ]; then
	python $WIKI_EXTRACT_PATH/WikiExtractor.py -o $DATA_PATH/$CHUNKED_ARTICLES_PATH -b $CHUNK_SIZE $DATA_PATH/$UNZIPPED_DATA_FILE >>log.txt;
	if [ $? -eq 0 ]; then
		echo successfully chunked data
		date > $DATA_PATH/$CHUNKED_ARTICLES_PATH/$SIGNAL_FILE
	else
		exit -1
	fi
fi

# Count vocab
if [ ! -e $DATA_PATH/$GRAM_W_COUNT_PATH/$SIGNAL_FILE ]; then
	mkdir -pv $DATA_PATH/$GRAM_W_COUNT_PATH
	find $DATA_PATH/$CHUNKED_ARTICLES_PATH/AA/* 2>>log.txt | xargs python grams_w_count.py -n $GRAM_W_COUNT_SIZE -o $DATA_PATH/$GRAM_W_COUNT_PATH 
	# python grams_w_count.py -n $GRAM_W_COUNT_SIZE -o $DATA_PATH/$GRAM_W_COUNT_PATH $DATA_PATH/$CHUNKED_ARTICLES_PATH/AA/*
	if [ $? -eq 0 ]; then
		echo successfully counted grams
		date > $DATA_PATH/$GRAM_W_COUNT_PATH/$SIGNAL_FILE
	else
		exit -1
	fi
fi
# Trim vocab
if [ ! -e $DATA_PATH/$GRAM_TRIM_PATH/$SIGNAL_FILE ]; then
	mkdir -pv $DATA_PATH/$GRAM_TRIM_PATH
	find $DATA_PATH/$GRAM_TRIM_PATH $DATA_PATH/$GRAM_W_COUNT_PATH/* 2>>log.txt | xargs python grams_trim.py -t $GRAM_TRIM_THRESHOLD -o $DATA_PATH/$GRAM_TRIM_PATH
	#python grams_trim.py -t $GRAM_TRIM_THRESHOLD -o $DATA_PATH/$GRAM_TRIM_PATH $DATA_PATH/$GRAM_W_COUNT_PATH/*
	if [ $? -eq 0 ]; then
		echo successfully trimmed vocabulary
		date > $DATA_PATH/$GRAM_TRIM_PATH/$SIGNAL_FILE
	else
		exit -1
	fi	
fi
# Collect vocab, reduce to one vocab file
if [ ! -e $GRAM_COLLECT_FILE ]; then
	mkdir -pv $DATA_PATH/$GRAM_COLLECT_PATH
	find $GRAM_COLLECT_FILE $DATA_PATH/$GRAM_TRIM_PATH/* 2>>log.txt | xargs python grams_reduce.py -t $GRAM_TRIM_THRESHOLD -o
	# python grams_reduce.py -t $GRAM_TRIM_THRESHOLD -o $GRAM_COLLECT_FILE $DATA_PATH/$GRAM_TRIM_PATH/*
	if [ $? -eq 0 ]; then
		echo successfully collected vocabulary
	else
		exit -1
	fi	
fi

# Tokenize articles
if [ ! -e $DATA_PATH/$TOKENIZED_PATH/$SIGNAL_FILE ]; then
	mkdir -pv $DATA_PATH/$TOKENIZED_PATH
	python tokenizer.py $DATA_PATH/$CHUNKED_ARTICLES_PATH $GRAM_COLLECT_FILE -o $DATA_PATH/$TOKENIZED_PATH
	if [ $? -eq 0 ]; then
		echo successfully tokenized dump
		date > $DATA_PATH/$TOKENIZED_PATH/$SIGNAL_FILE
	else
fi

# Collect Tokenized articles into raw text
if [ ! -e $DATA_PATH/$TOKENIZED_PATH/$PROCESSED_DUMP_NAME ]; then
	python generate_raw_gram_text.py -i $DATA_PATH/$TOKENIZED_PATH/articles -o $DATA_PATH/$TOKENIZED_PATH $PROCESSED_DUMP_NAME
	if [ $? -eq 0 ]; then
		echo successfully generated new dump
	else
fi

echo Finished Processing Data