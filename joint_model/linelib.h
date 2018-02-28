#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <vector>
#include <algorithm>
#include "ransampl.h"

#define MAX_STRING 100
#define EXP_TABLE_SIZE 1000
#define MAX_EXP 6
const int neg_table_size = 1e8;
const int hash_table_size = 30000000;

using namespace std;

typedef float real;

struct struct_node {
    double cn;
    char *word;
    double distinct;
    friend bool operator < (struct_node n_1, struct_node n_2)
    {
        return n_1.cn > n_2.cn;
    }
};

class line_node
{
protected:
    struct struct_node *node;
    int node_size, node_max_size, vector_size;
    char node_file[MAX_STRING];
    int *node_hash, *neg_table;
    real *vec;
    
    
    int get_hash(char *word);
    int add_node(char *word, double cn);
    int compare(const void *a, const void *b);
    void sort_node();
public:
    line_node();
    ~line_node();
    
    void init_neg_table();
    int get_vector_dim();
    int get_num_nodes();
    real *get_vector();
    struct struct_node *get_node();
    int get_neg_sample(int index);
    void init(char *file_name, int vector_dim);
    int search(char *word);
    void output(char *file_name, int binary);
    
    friend void linelib_output_batch(char *file_name, int binary, line_node **array_line_node, int cnt);
};

void linelib_output_batch(char *file_name, int binary, line_node **array_line_node, int cnt);

class line_link
{
protected:
    line_node *node_u, *node_v;
    real *expTable;
    ransampl_ws* ws;
    int neg_samples;
    char link_file[MAX_STRING];
    int ad_grad;
    double *grad_u, *grad_v;
public:
    long long edge_cnt;
    int *edge_u, *edge_v;
    double *edge_w, *edge_ori_w;

    line_link();
    ~line_link();
    
    int get_num_edges();
    void init(char *file_name, line_node *p_u, line_node *p_v, int negative, int adaptive_grad = 0);
    void densify(line_node *p_u, line_node *p_v, vector<pair<int, int> > expanded_pairs);

    void reweight(line_node *p_u, line_node *p_v);
    void aggregate_emb(line_node *p_to, line_node *p_from);
    real train_sample(real *error_vec, real alpha, double rand_num_1, double rand_num_2, unsigned long long &rand_index);
    void train_sample_square(real *error_vec, real alpha, double rand_num_1, double rand_num_2, unsigned long long &rand_index);

};