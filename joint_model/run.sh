# INPUT=/shared/data/tensor_embedding/data/dblp/frequent
INPUT=../data_news/
OUTPUT=../data_news/output_4/
# INPUT=../data_pubmed/
# OUTPUT=../data_pubmed/output_2/
# OUTPUT_AVG=../data_news/output/avg/
PTE_PATH=.
# options = main_dblp_heter.cpp, main_dblp_homo.cpp, main_yelp_heter.cpp, main_yelp_homo.cpp
# MAIN=$PTE_PATH/main_yelp_heter.cpp
# RESULT_VEC=$OUTPUT/pte_vec.txt
mkdir $OUTPUT
# mkdir $OUTPUT_AVG
make -s
cd -

# evaluate () {
# 	THREAD=5
# 	python ../transform_format.py -emb $1 -label $2 -output $OUTPUT/data_pte.txt -dim 300
# 	echo logistic regression:
# 	../liblinear/train -q -s 0 -v 5 -n 20 $OUTPUT/data_pte.txt
# 	echo linear svm:
# 	../liblinear/train -q -s 2 -v 5 -n 20 $OUTPUT/data_pte.txt
# }

evaluate () {
	echo start evaluate $1 millions training samples
	echo python $PTE_PATH/evaluate.py -fmode eval -emode FLAT -pmode COS -input ../data_news/output/
	python $PTE_PATH/evaluate.py -fmode eval -emode FLAT -pmode COS -input ../data_news/output/
	echo python $PTE_PATH/evaluate.py -fmode eval -emode FLAT -pmode DOT -input ../data_news/output/
	python $PTE_PATH/evaluate.py -fmode eval -emode FLAT -pmode DOT -input ../data_news/output/
	echo python $PTE_PATH/evaluate.py -fmode eval -emode FLAT -pmode COS -input ../data_news/output/avg/
	python $PTE_PATH/evaluate.py -fmode eval -emode FLAT -pmode DOT -input ../data_news/output/avg/
	echo python $PTE_PATH/evaluate.py -fmode eval -emode FLAT -pmode DOT -input ../data_news/output/avg/
	python $PTE_PATH/evaluate.py -fmode eval -emode FLAT -pmode DOT -input ../data_news/output/avg/
}

run () {
	echo start training pte
	$PTE_PATH/pte -path $INPUT -output $OUTPUT -binary 0 -size $1 -negative 3 -samples $2 -threads 20
	# echo === evaluating 4 research group labels ===
	# evaluate $RESULT_VEC $INPUT/label-group.txt
	# echo === evaluating 4 research area labels ===
	# evaluate $RESULT_VEC $INPUT/label-area.txt
}



run 4 50
# evaluate 15

# run 100 20
# evaluate 20

# run 100 30
# evaluate 30

# run 100 50
# evaluate 50

# run 100 100
# evaluate 100


# run 100 20
# evaluate 20

# # run 100 30
# # evaluate 30

# # run 100 50
# # evaluate 50

# run 100 100
# evaluate 100

# run 100 300
# evaluate 300

# python evaluate.py -fmode eval -emode FLAT -pmode COS -input ../data_news/output/






