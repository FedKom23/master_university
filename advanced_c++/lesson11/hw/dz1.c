#include <math.h>
#include <stdio.h>
#include <stdlib.h>

double f(double x)
{
    return 4.0 * (1.0 + sqrt(x)) * log(x) - 1.0;
}

double phi(double x)
{
    return exp(1.0 / (4.0 * (1.0 + sqrt(x))));
}

int main()
{
    double a, b;

    if (scanf("%lf %lf", &a, &b) != 2) {
        printf("no root\n");
        return 0;
    }

    if (a >= b) {
        printf("no root\n");
        return 0;
    }

    if (a <= 0) {
        printf("no root\n");
        return 0;
    }

    double fa = f(a);
    double fb = f(b);

    if (fa * fb > 0) {
        printf("no root\n");
        return 0;
    }

    double x0 = fabs((a + b) / 2.0);
    double x1 = fabs(phi(x0));

    double epsilon = 1e-5;

    while (fabs(x1 - x0) > epsilon) {
        x0 = x1;
        x1 = fabs(phi(x0));
    }
    printf("%.4lf\n", x1);

    return 0;
}