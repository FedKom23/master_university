#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

double func(double x)
{
    return x * log(x) + 2 * x * cos(x);
}

double simpson(double a, double b, double (*f)(double), int n)
{
    double h = (b - a) / n;
    double sum = f(a) + f(b);

    for (int i = 1; i < n; i++) {
        double x = a + i * h;
        if (i % 2 == 0) {
            sum += 2 * f(x);
        } else {
            sum += 4 * f(x);
        }
    }

    return sum * h / 3;
}

int main()
{
    double a, b;
    if (scanf("%lf %lf", &a, &b) != 2) {
        return 1;
    }
    printf("%.3lf\n", simpson(a, b, func, 100));

    return 0;
}