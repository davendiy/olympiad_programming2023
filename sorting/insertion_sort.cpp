#include <vector>
#include <iostream>


void insertion_sort(std::vector<int> &array){ 
    
    int n = array.size(); 
    for (int i = 0; i < n; i++){ 
        int cur_element = array[i];
        int cur_position = i - 1;

        // insert chosen element to the sorted left part of the array
        while (cur_position >= 0 && array[cur_position] > cur_element){ 
            array[cur_position + 1] = array[cur_position]; 
            cur_position--; 
        }
        array[cur_position + 1] = cur_element;
    }
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

    insertion_sort(test_array); 

    for (int i = 0; i < n; i++){ 
        std::cout << test_array[i] << " "; 
    }

    std::cout << std::endl;
}