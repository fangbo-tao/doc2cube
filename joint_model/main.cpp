//  Copyright 2013 Google Inc. All Rights Reserved.
//
//  Licensed under the Apache License, Version 2.0 (the "License");
//  you may not use this file except in compliance with the License.
//  You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
//  Unless required by applicable law or agreed to in writing, software
//  distributed under the License is distributed on an "AS IS" BASIS,
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  See the License for the specific language governing permissions and
//  limitations under the License.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <vector>
#include <math.h>
#include <algorithm>
#include <time.h>
#include <set>
#include <pthread.h>
#include <gsl/gsl_rng.h>
#include "linelib.h"
#include "utils.h"

char file_path[MAX_STRING], output_path[MAX_STRING];
int binary = 0, num_threads = 1, vector_size = 100, negative = 5;
long long samples = 1, edge_count_actual;
real alpha = 0.025, starting_alpha;

using namespace std;


const gsl_rng_type * gsl_T;
gsl_rng * gsl_r;
ransampl_ws* ws;

line_node node_d, node_l, node_p;
line_link link_lp, link_dp;

void *TrainModelThread(void *id) {
    long long edge_count = 0, last_edge_count = 0;
    unsigned long long next_random = (long long)id;
    real *error_vec = (real *)calloc(vector_size, sizeof(real));
    real e_total = 0;
    
    while (1)
    {
        //judge for exit
        if (edge_count > samples / num_threads + 2) break;
        
        if (edge_count - last_edge_count>10000)
        {
            edge_count_actual += edge_count - last_edge_count;
            last_edge_count = edge_count;
            printf("%cAlpha: %f Progress: %.3lf%%, Error: %.3lf", 13, alpha, (real)edge_count_actual / (real)(samples + 1) * 100, e_total);
            fflush(stdout);
            e_total = 0;
            alpha = starting_alpha * (1 - edge_count_actual / (real)(samples + 1));
            if (alpha < starting_alpha * 0.0001) alpha = starting_alpha * 0.0001;
        }
        
        // here lp is sampled much smaller
        // if (edge_count % 10 == 0)
        e_total += link_lp.train_sample(error_vec, alpha, gsl_rng_uniform(gsl_r), gsl_rng_uniform(gsl_r), next_random);
        e_total += link_dp.train_sample(error_vec, alpha, gsl_rng_uniform(gsl_r), gsl_rng_uniform(gsl_r), next_random);
        
        edge_count++;
    }
    free(error_vec);
    pthread_exit(NULL);
}

void comp_node_distinct(double ratio, map<string, string> top_label_map) {
    int a, i;
    int d_cnt = node_d.get_num_nodes(), l_cnt = node_l.get_num_nodes();
    int p_cnt = node_p.get_num_nodes();

    // label related
    int TOP_CNT = 5;
    int label_cnt[5] = {0};
    map<string, int> top_label_to_idx;
    top_label_to_idx["Arts"] = 0;
    top_label_to_idx["Sports"] = 1;
    top_label_to_idx["Business"] = 2;
    top_label_to_idx["Politics"] = 3;
    top_label_to_idx["Science"] = 4;
    double normalizer = 1.609439;


    map<int, int> doc_label_map;
    map<int, double> doc_similar_score;
    for (a = 0; a < d_cnt; a++) {
        char max_label[MAX_STRING];
        double max_score = -1.0;
        string top_label;
        double sim = 0;
        
        for (i = 0; i < l_cnt; i++) {
            sim = CosSim(&(node_d.get_vector()[a * vector_size]), &(node_l.get_vector()[i * vector_size]), vector_size);
            // printf("%d %lf\n", i, sim);
            if (sim > max_score) {
                max_score = sim;
                strcpy(max_label, node_l.get_node()[i].word);
            }
        }
        top_label = top_label_map[string(max_label)];
        doc_label_map[a] = top_label_to_idx[top_label];
        doc_similar_score[a] = max_score;
    }

    map<int, int> doc_label_map_filtered;
    int cnt = 0;
    
    // select top confident docs
    for (auto& x : doc_similar_score)
    {
        if (x.second > ratio) {
            cnt += 1;
            doc_label_map_filtered[x.first] = doc_label_map[x.first];
            label_cnt[doc_label_map[x.first]] += 1;
        }
    }


    printf("%d docs are confident.\n", cnt);

    for (int j = 0; j < TOP_CNT; ++j)
    {
        std::cout << j << ": " <<  label_cnt[j] << std::endl;
    }    

    double p_dist[p_cnt][TOP_CNT];
    for (a = 0; a != p_cnt; a++) for (i = 0; i != TOP_CNT; i++) p_dist[a][i] = 0;
    for (a = 0; a < link_dp.edge_cnt; a++) {
        int d_id = link_dp.edge_u[a];
        int p_id = link_dp.edge_v[a];
        if (doc_label_map_filtered.count(d_id) > 0)
            p_dist[p_id][doc_label_map_filtered[d_id]] += 1;
    }

    double uniform_vec[TOP_CNT];
    fill_n(uniform_vec, TOP_CNT, 1.0/TOP_CNT);
    map<int, double> p_kl;
    for (a = 0; a < p_cnt; a ++ ) {
        double sum = 0;

        // for (int j = 0; j < TOP_CNT; ++j)
        // {
        //     std::cout << p_dist[a][j] << ' ' <<  uniform_vec[j] << ' ' << std::endl;
        // }

        for (i = 0; i < TOP_CNT; i++) sum += p_dist[a][i];
        if (sum > 0)
            for (i = 0; i < TOP_CNT; i++) p_dist[a][i] /= sum;
        else
            for (i = 0; i < TOP_CNT; i++) p_dist[a][i] = 1.0/TOP_CNT;
        

        p_kl[a] = KLDivergence(p_dist[a], uniform_vec, TOP_CNT) / normalizer;
        // printf("%s %lf\n", node_p.get_node()[a].word, p_kl[a]);
        node_p.get_node()[a].distinct = p_kl[a];
    }
}


vector<pair<int, int> > extend_seeds(int total_limit, int cate_limt, double multiplier) {
    int a, i, l_id, p_id;
    int d_cnt = node_d.get_num_nodes(), l_cnt = node_l.get_num_nodes();
    int p_cnt = node_p.get_num_nodes();

    // all the existing seeds
    map<int, int> p_to_best_l; 
    map<int, vector<int> > label_to_seeds;
    set<int> seed_ps;
    double rel_scores[p_cnt][l_cnt];// = {{0}};
    memset( rel_scores, 0, p_cnt*l_cnt*sizeof(double) );
    double expan_scores[p_cnt];
    double expan_scores_backup[p_cnt];
    memset( expan_scores, 0, p_cnt*sizeof(double) );

    for (a = 0; a < link_lp.edge_cnt; a++) {
        l_id = link_lp.edge_u[a];
        p_id = link_lp.edge_v[a];
        label_to_seeds[l_id].push_back(p_id);
        seed_ps.insert(p_id);
    }
    printf("This LP have %d seeds", link_lp.edge_cnt);

    // for (auto& x : label_to_seeds)
    // {
    //  std::cout << x.first << "," << x.second[0] << std::endl;
    // }

    vector<int> tmp_seeds;
    double sim = 0.0, max_sim = -multiplier, max_rel=0;
    int max_idx = 0;
    set<int>::iterator it;
    for (a = 0; a < p_cnt; a++) {

        for (i = 0; i < l_cnt; i++) {
            tmp_seeds = label_to_seeds[i];
            max_sim = -multiplier;
            for (auto & s : tmp_seeds) {
                
                sim = multiplier * CosSim(&(node_p.get_vector()[a * vector_size]), &(node_p.get_vector()[s * vector_size]), vector_size);
                if (sim > max_sim) max_sim = sim;
            }
            rel_scores[a][i] = max_sim;
        }

        SoftMax(rel_scores[a], l_cnt);

        max_rel = 0;
        max_idx = 0;
        for (i = 0; i < l_cnt; i++)
            if (rel_scores[a][i] > max_rel) {max_idx = i; max_rel = rel_scores[a][i];}
        p_to_best_l[a] = max_idx;
        expan_scores[a] = max_rel;
        
        // compute popularity
        expan_scores[a] *= 3 + log(1 + node_p.get_node()[a].cn);
        expan_scores_backup[a] = expan_scores[a];
        it = seed_ps.find(a);
        if (it != seed_ps.end()) expan_scores[a] = 0;

        // cout << node_p.get_node()[a].word << " " << node_l.get_node()[p_to_best_l[a]].word
        //     << " " << expan_scores[a] << endl;

        // if (strcmp(node_p.get_node()[a].word, "song") == 0) {
        //     for (i = 0; i < l_cnt; i++)
        //         printf("%ld ", rel_scores[a][i]);
        //     printf("\n the relevance scores === \n");
        //     for (i = 0; i < l_cnt; i++)
        //         printf("%ld ", rel_scores[a][i]);
        // }
    }

    map<int, int> label_expan_cnt;
    for (i = 0; i < l_cnt; i++) {
        label_expan_cnt[i] = 0;
    }


    int exp_cnt = 0, label = 0;
    vector<pair<int, int> > expanded_pairs;

    while (exp_cnt < total_limit) {
        max_sim = 0;
        max_idx = -1;
        for (a = 0; a < p_cnt; a++)
            if (expan_scores[a] > max_sim) {max_sim = expan_scores[a]; max_idx = a;}
        label = p_to_best_l[max_idx];
        expan_scores[max_idx] = 0;
        if (label_expan_cnt[label] >= cate_limt)
            continue;
        else {
            expanded_pairs.push_back(make_pair(label, max_idx));
            label_expan_cnt[label] += 1;
            exp_cnt += 1;
        }
    }

    // vector<pair<int, int>>::const_iterator iterator;
    std::cout << "expanding words =================" << std::endl;
    for (i = 0; i < total_limit; i++) {
        std::cout << node_l.get_node()[expanded_pairs[i].first].word << ' '
            << node_p.get_node()[expanded_pairs[i].second].word << ' ' << 
            expan_scores_backup[expanded_pairs[i].second] << endl;
    }
    std::cout << "expanding words DONE =================" << std::endl;

    return expanded_pairs;
}

void TrainModel() {
    long a, b;
    FILE *fo;
    pthread_t *pt = (pthread_t *)malloc(num_threads * sizeof(pthread_t));
    starting_alpha = alpha;
    char file_name[MAX_STRING];

    printf("Start loading node files...\n");
    
    sprintf(file_name, "%sd.txt", file_path);
    node_d.init(file_name, vector_size);
    sprintf(file_name, "%sl.txt", file_path);
    // node_l.init(file_name, vector_size);
    // sprintf(file_name, "%sl_2.txt", file_path);
    node_l.init(file_name, vector_size);
    sprintf(file_name, "%sp.txt", file_path);
    node_p.init(file_name, vector_size);

    printf("Start loading link files...\n");
    
    sprintf(file_name, "%sdp.txt", file_path);
    link_dp.init(file_name, &node_d, &node_p, negative);
    sprintf(file_name, "%slp.txt", file_path);
    // link_lp.init(file_name, &node_l, &node_p, negative);
    // sprintf(file_name, "%slp_2.txt", file_path);
    link_lp.init(file_name, &node_l, &node_p, negative);

    sprintf(file_name, "%sl_mapping.txt", file_path);
    // map<string, string> top_label_map = ReadLabelMapping(file_name);
    // sprintf(file_name, "%sl_2_mapping.txt", file_path);
    map<string, string> top_label_map = ReadLabelMapping(file_name);

    // init token neg 
    printf("Start init neg...\n");
    node_p.init_neg_table();
    
    gsl_rng_env_setup();
    gsl_T = gsl_rng_rand48;
    gsl_r = gsl_rng_alloc(gsl_T);
    gsl_rng_set(gsl_r, 314159265);

    
    clock_t start = clock();
    printf("Loading done.\nTraining process:\n");
    for (a = 0; a < num_threads; a++) pthread_create(&pt[a], NULL, TrainModelThread, (void *)a);
    for (a = 0; a < num_threads; a++) pthread_join(pt[a], NULL);
    printf("\n");
    clock_t finish = clock();
    printf("Total time: %lf\n", (double)(finish - start) / CLOCKS_PER_SEC);

    
    int iterate = 0;

    while (iterate < 1) {

        // reweight D-P network
        if (false) {
            // here needs to retrain
            comp_node_distinct(0.92, top_label_map);
            // update the network 
            link_dp.reweight(&node_d, &node_p);
            // node_p.init_neg_table();
            // learning
            // exit(1);
            alpha = 0.025;
            edge_count_actual = 0;
            clock_t start = clock();
            printf("Loading done.\nTraining process:\n");
            for (a = 0; a < num_threads; a++) pthread_create(&pt[a], NULL, TrainModelThread, (void *)a);
            for (a = 0; a < num_threads; a++) pthread_join(pt[a], NULL);
            printf("\n");
            clock_t finish = clock();
            printf("Total time: %lf\n", (double)(finish - start) / CLOCKS_PER_SEC);
        }

        // densify L-P network
        if (false) {
            link_lp.densify(&node_l, &node_p, extend_seeds(20, 2, 5.0));
            alpha = 0.025;
            edge_count_actual = 0;
            clock_t start = clock();
            printf("Loading done.\nTraining process:\n");
            for (a = 0; a < num_threads; a++) pthread_create(&pt[a], NULL, TrainModelThread, (void *)a);
            for (a = 0; a < num_threads; a++) pthread_join(pt[a], NULL);
            printf("\n");
            clock_t finish = clock();
            printf("Total time: %lf\n", (double)(finish - start) / CLOCKS_PER_SEC);
        }

        iterate += 1;

    }

    // link_lp.aggregate_emb(&node_l, &node_p);
    // link_dp.aggregate_emb(&node_d, &node_p);
    
    sprintf(file_name, "%sd.vec", output_path);
    node_d.output(file_name, binary);
    sprintf(file_name, "%sl.vec", output_path);
    node_l.output(file_name, binary);
    sprintf(file_name, "%sp.vec", output_path);
    node_p.output(file_name, binary);

    // // here needs to retrain
    // comp_node_distinct(0.9, top_label_map);
    // // update the network 
    // link_dp.reweight(&node_d, &node_p);
    // link_lp.aggregate_emb(&node_l, &node_p);
    // link_dp.aggregate_emb(&node_d, &node_p);

    // sprintf(file_name, "%savg/d.vec", output_path);
    // node_d.output(file_name, binary);
    // sprintf(file_name, "%savg/l.vec", output_path);
    // node_l.output(file_name, binary);
    // sprintf(file_name, "%savg/p.vec", output_path);
    // node_p.output(file_name, binary);

    
}

int ArgPos(char *str, int argc, char **argv) {
    int a;
    for (a = 1; a < argc; a++) if (!strcmp(str, argv[a])) {
        if (a == argc - 1) {
            printf("Argument missing for %s\n", str);
            exit(1);
        }
        return a;
    }
    return -1;
}

int main(int argc, char **argv) {
    int i;
    if (argc == 1) {
        printf("LINE: Large Information Network Embedding toolkit v 0.1b\n\n");
        printf("Options:\n");
        printf("Parameters for training:\n");
        printf("\t-path <file>\n");
        printf("\t\tUse network data from <file> to train the model\n");
        printf("\t-output <file>\n");
        printf("\t\tUse <file> to save the resulting vectors\n");
        printf("\t-debug <int>\n");
        printf("\t\tSet the debug mode (default = 2 = more info during training)\n");
        printf("\t-binary <int>\n");
        printf("\t\tSave the resulting vectors in binary moded; default is 0 (off)\n");
        printf("\t-size <int>\n");
        printf("\t\tSet size of word vectors; default is 100\n");
        printf("\t-order <int>\n");
        printf("\t\tThe type of the model; 1 for first order, 2 for second order; default is 2\n");
        printf("\t-negative <int>\n");
        printf("\t\tNumber of negative examples; default is 5, common values are 5 - 10 (0 = not used)\n");
        printf("\t-samples <int>\n");
        printf("\t\tSet the number of training samples as <int>Million\n");
        printf("\t-threads <int>\n");
        printf("\t\tUse <int> threads (default 1)\n");
        printf("\t-alpha <float>\n");
        printf("\t\tSet the starting learning rate; default is 0.025\n");
        printf("\nExamples:\n");
        printf("./line -train net.txt -output vec.txt -debug 2 -binary 1 -size 200 -order 2 -negative 5 -samples 100\n\n");
        return 0;
    }
    output_path[0] = 0;
    if ((i = ArgPos((char *)"-path", argc, argv)) > 0) strcpy(file_path, argv[i + 1]);
    if ((i = ArgPos((char *)"-output", argc, argv)) > 0) strcpy(output_path, argv[i + 1]);
    if ((i = ArgPos((char *)"-binary", argc, argv)) > 0) binary = atoi(argv[i + 1]);
    if ((i = ArgPos((char *)"-size", argc, argv)) > 0) vector_size = atoi(argv[i + 1]);
    if ((i = ArgPos((char *)"-negative", argc, argv)) > 0) negative = atoi(argv[i + 1]);
    if ((i = ArgPos((char *)"-samples", argc, argv)) > 0) samples = atoi(argv[i + 1])*(long long)(1000000);
    if ((i = ArgPos((char *)"-alpha", argc, argv)) > 0) alpha = atof(argv[i + 1]);
    if ((i = ArgPos((char *)"-threads", argc, argv)) > 0) num_threads = atoi(argv[i + 1]);
    TrainModel();
    return 0;
}