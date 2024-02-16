
#include <vector>
#include <iostream>


/* 
 * Merge two sorted sub-arrays inplace.
 * Note: subarrays from `start` to `mid` and from `mid` to `end` inclusively. 
 */
void merge(std::vector<int> &arr, int start, int mid, int end){
    std::vector<int> left_arr, right_arr; 

    // copy subarrays into temporary ones 
    for (int i = start; i <= mid; i++) left_arr.push_back(arr[i]); 
    for (int i = mid + 1; i <= end; i++) right_arr.push_back(arr[i]); 

    // where to place next element in the initial array
    int cur_position = start; 
    int i = 0, j = 0;
    
    // while two arrays not empty, compare their first elements
    while (i < left_arr.size() && j < right_arr.size()){ 
        if (left_arr[i] <= right_arr[j]) {
            arr[cur_position] = left_arr[i]; 
            i++;
        } else{ 
            arr[cur_position] = right_arr[j]; 
            j++;
        }
        cur_position++;
    }

    // merge remain arrays without comparing   
    while ( i < left_arr.size() ){
        arr[cur_position] = left_arr[i]; 
        i++; 
        cur_position++;
    }

    while ( j < right_arr.size() ){
        arr[cur_position] = right_arr[j]; 
        j++; 
        cur_position++;
    }

}


void merge_sort(std::vector<int> &arr, int start, int end){ 
    if (start >= end) return; 

    int mid = start + (end - start) / 2; 
    merge_sort(arr, start, mid); 
    merge_sort(arr, mid + 1, end); 
    merge(arr, start, mid, end);

}


int main(){ 
    int n; 
    std::vector<int> test_array; 

    std::cin >> n; 
    for (int i = 0; i < n; i++) {
        int tmp; 
        std::cin >> tmp; 
        test_array.push_back(tmp); 
    }

    merge_sort(test_array, 0, n-1); 

    for (int i = 0; i < n; i++){ 
        std::cout << test_array[i] << " "; 
    }

    std::cout << std::endl;
}