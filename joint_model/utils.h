#include <map>
#include <string>
#include <math.h>
#include <iostream>
#include <stdio.h>
#include <stdlib.h>

#define MAX_STRING 100
typedef float real;

double CosSim(real *p, real *q, int vec_size);
double KLDivergence(double *p, double *q, int vec_size);
double* SoftMax(double* p, int vec_size);
std::map<std::string, std::string> ReadLabelMapping(char *file_name);

