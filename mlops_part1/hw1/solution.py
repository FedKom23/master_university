cmd_task1_count_files = "ls -l | grep -v ^d | grep -v ^total| wc -l"

cmd_task2_biggest_files = "du -h * | sort -rh | cut -f2 | head -n 5"

cmd_task3_sort_unique = "sort -u input.txt > clean.txt"

cmd_task4_grep_error = 'grep -h "ERROR" *.log | cut -b 1- | sort -u'

cmd_task5_empty_files = "find . -maxdepth 1 -type f -empty"
