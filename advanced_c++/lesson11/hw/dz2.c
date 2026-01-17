#include <math.h>
#include <stdio.h>
#include <stdlib.h>

double f(double x)
{
    return sin(x) - (1 / x);
}

double proizv(double x, double eps)
{
    return (f(x + eps) - f(x)) / eps;
}

double newton(double a, double b, double eps)
{
    double x = (a + b) / 2;
    while (fabs(f(x)) > eps) {
        x = x - f(x) / proizv(x, eps);
    }
    return x;
}

int main()
{
    double a, b;

    if (scanf("%lf %lf", &a, &b) != 2) {
        return 0;
    }

    double epsilon = 1e-5;
    double x = newton(a, b, epsilon);
    printf("%.4lf\n", x);

    return 0;
}