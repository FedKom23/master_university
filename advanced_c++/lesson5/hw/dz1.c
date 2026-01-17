video_file_t** sort_video_files(const video_file_t** files,
    is_less_func_t is_less_func,
    copy_func_t copy_func,
    malloc_func_t malloc_func)
{
    int count = 0;
    while (files[count] != NULL) {
        count++;
    }

    video_file_t** sorted_files = malloc_func((count + 1) * sizeof(video_file_t*));
    if (sorted_files == NULL) {
        return NULL;
    }

    for (int i = 0; i < count; i++) {
        sorted_files[i] = malloc_func(sizeof(video_file_t));
        copy_func(sorted_files[i], files[i]);
    }
    sorted_files[count] = NULL;

    for (int i = 0; i < count - 1; i++) {
        for (int j = 0; j < count - i - 1; j++) {
            if (is_less_func(sorted_files[j + 1], sorted_files[j])) {
                video_file_t* temp = sorted_files[j];
                sorted_files[j] = sorted_files[j + 1];
                sorted_files[j + 1] = temp;
            }
        }
    }

    return sorted_files;
}