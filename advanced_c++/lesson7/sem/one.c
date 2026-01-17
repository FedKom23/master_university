#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

int main()
{
    int N, M;

    if (scanf("%d\n", &N) != 1)
        return 1;

    int c;

    static int first_len[100001] = { 0 };
    static int cnt_len[100001] = { 0 };
    static int first_letter[26] = { 0 };
    static int cnt_letter[26] = { 0 };

    for (int i = 1; i <= N; ++i) {
        unsigned long seen = 0UL;
        int L = 0;

        while (1) {
            c = getchar();
            if (c == '\n' || c == EOF) {
                break;
            }
            if (c >= 'a' && c <= 'z') {
                unsigned long bit = 1UL << (c - 'a');
                if ((seen & bit) == 0) {
                    seen |= bit;
                }
                L++;
            }
        }

        if (L <= 10000) {
            if (first_len[L] == 0)
                first_len[L] = i;
            cnt_len[L]++;
        }

        for (int a = 0; a < 26; ++a) {
            unsigned long bit = 1UL << a;
            if (seen & bit) {
                if (first_letter[a] == 0)
                    first_letter[a] = i;
                cnt_letter[a]++;
            }
        }
    }

    if (scanf("%d\n", &M) != 1)
        return 1;

    for (int _ = 0; _ < M; ++_) {
        int mode = 0;
        int len = 0;
        int letter = -1;

        while (1) {
            c = getchar();
            if (c == '\n' || c == EOF) {
                break;
            }

            if (mode == 0) {
                if (c == 'S')
                    mode = 1;
                else if (c == 'L')
                    mode = 2;
                continue;
            }

            if (mode == 1) {
                if (c >= '0' && c <= '9')
                    len = len * 10 + (c - '0');
            } else if (mode == 2) {
                if (letter == -1 && c >= 'a' && c <= 'z')
                    letter = c - 'a';
            }
        }

        if (mode == 1) {
            if (len >= 0 && len <= 10000 && cnt_len[len] > 0)
                printf("%d,%d\n", first_len[len], cnt_len[len]);
            else
                printf("NO!\n");
        } else if (mode == 2) {
            if (letter >= 0 && cnt_letter[letter] > 0)
                printf("%d,%d\n", first_letter[letter], cnt_letter[letter]);
            else
                printf("NO!\n");
        }
    }

    return 0;
}