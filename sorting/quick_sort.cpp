

#include <iostream> 
#include <vector>


/* 
 * Auxiliary function for swapping two elements. 
 */
void swap_aux(std::vector<int> &arr, int i, int j){
    int tmp = arr[i]; 
    arr[i] = arr[j]; 
    arr[j] = tmp;
}


/*
 * Divide array into two parts: elements greater than chosen and less respectively. 
 */
int partition(std::vector<int> &arr, int start, int end){ 
    
    // choose the first one as pivot. 
    // possible improvement: use median of random sample of 3 elements as pivot
    int pivot = arr[start]; 
    int count = 0; 

    for (int i = start + 1; i <= end; i++){
        if (arr[i] <= pivot) count++;
    }

    // correct position -- right after the elements of array became greater
    int pivot_index = start + count; 
    swap_aux(arr, pivot_index, start);

    int i = start, j = end; 

    while (i < pivot_index && j > pivot_index) {
        while (arr[i] <= pivot) i++; 
        while (arr[j] > pivot) j--; 

        if (i < pivot_index && j > pivot_index) { 
            swap_aux(arr, i, j); 
            i++; 
            j--;
        }
    }

    return pivot_index;
}


void quick_sort(std::vector<int> &arr, int start, int end){ 
    if (start >= end) return; 
    
    // possible improvement: shuffle before sorting
    int p = partition(arr, start, end); 
    quick_sort(arr, start, p-1); 
    quick_sort(arr, p+1, end);
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

    quick_sort(test_array, 0, n-1); 

    for (int i = 0; i < n; i++){ 
        std::cout << test_array[i] << " "; 
    }

    std::cout << std::endl;
}