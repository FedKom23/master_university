#include <ctype.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int is_valid_sudoku(int grid[9][9])
{
    int row[9][10] = { 0 };
    int col[9][10] = { 0 };
    int kvadrat[9][10] = { 0 };

    for (int i = 0; i < 9; i++) {
        for (int j = 0; j < 9; j++) {
            int num = grid[i][j];
            if (num < 1 || num > 9) {
                return 0;
            }
            if (row[i][num]) {
                return 0;
            }
            row[i][num] = 1;

            if (col[j][num]) {
                return 0;
            }
            col[j][num] = 1;

            int box_index = (i / 3) * 3 + (j / 3);
            if (kvadrat[box_index][num]) {
                return 0;
            }
            kvadrat[box_index][num] = 1;
        }
    }
    return 1;
}

int main()
{
    int grid[9][9];

    for (int i = 0; i < 9; i++) {
        for (int j = 0; j < 9; j++) {
            if (scanf("%d", &grid[i][j]) != 1)
                return 1;
        }
    }

    if (is_valid_sudoku(grid)) {
        printf("valid\n");
    } else {
        printf("invalid\n");
    }

    return 0;
}