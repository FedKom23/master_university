const char* cool_strstr(const char* str1, const char* str2)
{
    if (str2[0] == '\0') {
        return str1;
    }
    for (int i = 0; str1[i] != '\0'; i++) {
        int j = 0;
        while (str1[i + j] == str2[j]) {
            j++;
            if (str2[j] == '\0') {
                return &str1[i];
            }
        }
    }
    return ((void*)0);
}