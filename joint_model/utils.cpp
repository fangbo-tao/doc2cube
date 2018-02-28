#include "utils.h"

std::map<std::string, std::string> ReadLabelMapping(char *file_name) {
	std::map<std::string, std::string> top_label_map;

	FILE *fi = fopen(file_name, "rb");
    if (fi == NULL)
    {
        printf("ERROR: Label Mapping File not found!\n");
        printf("%s\n", file_name);
    }

    char label_from[MAX_STRING], label_to[MAX_STRING];

    while (1)   
    {
        if (fscanf(fi, "%s\t%s", label_from, label_to) != 2) break;
        // std::cout << "XXX" << label_from << std::endl;
        top_label_map[std::string(label_from)] = std::string(label_to);
    }
    fclose(fi);

 //    for (auto& x : top_label_map)
	// {
 //    	std::cout << x.first << "," << x.second << std::endl;
	// }

    return top_label_map;
}

double CosSim(real *p, real *q, int vec_size) {
	double det = 0, p_len = 0, q_len = 0;
	for (int i = 0; i < vec_size; i++) {
		det += p[i] * q[i];
		p_len += p[i] * p[i];
		q_len += q[i] * q[i];
	}
	return det / (sqrt(p_len) * sqrt(q_len));
}

double KLDivergence(double *p, double *q, int vec_size) {
	double entropy = 0;
	for (int i = 0; i < vec_size; i++)
		if (p[i] > 0)
			entropy += p[i] * log(p[i] / q[i]);
	return entropy;
}

double* SoftMax(double* p, int vec_size) {
	double exp_sum = 0;
	for (int i = 0; i < vec_size; i++) exp_sum += exp(p[i]);
	for (int i = 0; i < vec_size; i++) p[i] = exp(p[i]) / exp_sum;
}






