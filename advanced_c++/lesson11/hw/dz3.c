#include <math.h>
#include <stdio.h>
#include <stdlib.h>

double f(double x, double y)
{
    return ((y - log(x)) / x);
}

double eiler(double x0, double y0, double b, double eps)
{
    double x = x0;
    double y = y0;
    while (x < b) {
        y = y + eps * f(x, y);
        x = x + eps;
    }
    return y;
}

int main()
{
    double a, b, c;

    if (scanf("%lf %lf %lf", &a, &b, &c) != 3) {
        return 0;
    }

    double epsilon = 1e-6;
    double y_b = eiler(a, c, b, epsilon);
    printf("%0.4lf\n", y_b);
    return 0;
}