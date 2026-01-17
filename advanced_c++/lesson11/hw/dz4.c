#include <math.h>
#include <stdio.h>
#include <stdlib.h>

double sign(double x)
{
    if (x > 0)
        return 1.0;
    if (x < 0)
        return -1.0;
    return 0.0;
}

double f(double x, double y)
{
    return 3 * pow(x, 2) + x * y + 2 * pow(y, 2) - x - 4 * y;
}

double f_x(double x, double y)
{
    return 6 * x + y - 1;
}

double f_y(double x, double y)
{
    return x + 4 * y - 4;
}

void gradient_spusk(double start_x, double start_y, double epsilon,
    double* result_x, double* result_y)
{
    double x = start_x;
    double y = start_y;
    double learning_rate = 0.01;
    int first_flg = 1;

    double dx = 0, dy = 0;

    while (first_flg == 1 || (sqrt(dx * dx + dy * dy) > epsilon)) {
        if (first_flg == 1) {
            first_flg = 0;
        }
        double old_x = x;
        double old_y = y;

        double grad_x = f_x(x, y);
        double grad_y = f_y(x, y);

        x = old_x - learning_rate * grad_x;
        y = old_y - learning_rate * grad_y;

        dx = x - old_x;
        dy = y - old_y;
    }

    *result_x = x;
    *result_y = y;
}

int main()
{
    double a, b;

    if (scanf("%lf %lf", &a, &b) != 2) {
        return 1;
    }

    double epsilon = 1e-7;
    double x, y;
    gradient_spusk(a, b, epsilon, &x, &y);
    if (sign(x) == -1) {
        x = x * (-1);
    }
    printf("%.3lf %.3lf\n", x, y);
    return 0;
}