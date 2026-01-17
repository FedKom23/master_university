#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

int main()
{

    int numBottles;
    int numExchange;

    if (scanf("%d %d", &numBottles, &numExchange) != 2) {
        return 1;
    }
    int result = 0;
    while (true) {

        int cel = numBottles / numExchange;
        if (cel == 0) {
            result += numBottles % numExchange;
            break;
        };
        result += cel * numExchange;
        numBottles = cel + numBottles % numExchange;
    };
    printf("%d", result);
    return 0;
};