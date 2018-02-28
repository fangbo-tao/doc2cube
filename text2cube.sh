#!/bin/bash

export PYTHON=python
export PYPY=python
if type "pypy" > /dev/null; then
	export PYPY=pypy
fi

TEXT='data/news_parsed.txt'
META='data/news_meta_topic.txt'
EVAL='data/news_eval.txt'

OUTPUT='tmp/'
EMB_SIZE=100
SAMPLE=10


rm -r tmp
mkdir tmp
mkdir results

# create L-P-D network given segmented text and dimension values
echo ========= Preparing network data - Step 1....
${PYPY} ./src/prel.py -text ${TEXT} -meta ${META} -output ${OUTPUT}
echo ========= Preparing network data - Step 2....
${PYPY} ./src/parse_flat.py -text ${TEXT} -folder ${OUTPUT}


echo ========= Learning joint embedding....
cd joint_model
make
cd ..
joint_model/pte -path ${OUTPUT} -output ${OUTPUT} -binary 0 -size ${EMB_SIZE} -negative 3 -samples ${SAMPLE} -threads 20


echo ========= Evaluating raw embedding
${PYPY} ./src/evaluate.py -fmode eval -emode FLAT -pmode COS -eval ${EVAL} -folder tmp/

echo ========= Adjusting document embedding....
${PYPY} ./src/evaluate.py -fmode reweight -emode FLAT -pmode COS -eval ${EVAL} -folder tmp/

# echo ========= Adjusting label embedding....
# ${PYPY} ./src/evaluate.py -fmode expan -emode FLAT -pmode COS -eval ${EVAL} -folder tmp/

