video_file_t** filter_video_files(const video_file_t** files,
    filter_func_t filter_func,
    copy_func_t copy_func,
    malloc_func_t malloc_func)
{
    int sum_flg = 0;
    const video_file_t** checker = files;
    while (*checker != NULL) {
        if (filter_func(*checker) != 0) {
            sum_flg++;
        }
        checker++;
    }
    if (sum_flg == 0) {
        return NULL;
    }
    video_file_t** new_files = malloc_func((sum_flg + 1) * sizeof(video_file_t*));
    int i = 0;
    checker = files;
    while (*checker != 0) {
        if (filter_func(*checker) != 0) {
            new_files[i] = malloc_func(sizeof(video_file_t));
            copy_func(new_files[i], *checker);
            i++;
        }
        checker++;
    }
    new_files[i] = NULL;
    return new_files;
}