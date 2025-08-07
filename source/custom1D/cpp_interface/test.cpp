


#include <iostream>
#include <windows.h>



const int test_array_length = 1000*4000;
float test_array[test_array_length];

float* array_pointer;
int parent_pid;
uintptr_t pointer_to_parent_array;


int main()
{
    std::fill(std::begin(test_array), std::end(test_array), 33.3);
    std::cout << "dll_main\n";

    return 0;
}





extern "C" __declspec(dllexport) void dll_main()
{
    main();
}





void get_parent_array(char buffer[sizeof(float) * test_array_length], SIZE_T buffer_size)
{
    HANDLE hProcess = OpenProcess(PROCESS_VM_READ, FALSE, parent_pid);
    if (hProcess == NULL)
    {
        std::cerr << "Failed to open process." << std::endl;
    }
    SIZE_T bytesRead;
    LPCVOID addressToRead = (LPCVOID)pointer_to_parent_array; // Replace with the desired address
    if (ReadProcessMemory(hProcess, addressToRead, buffer, buffer_size, &bytesRead))
    {
        //std::cout << "Read " << bytesRead << " bytes: " << buffer << std::endl;
    }
    else
    {
        std::cerr << "Failed to read memory." << std::endl;
    }
    CloseHandle(hProcess);

}


extern "C" __declspec(dllexport) void setup_array_pointer(uintptr_t pointer_to_array, int pid)
{
    parent_pid = pid;
    pointer_to_parent_array = pointer_to_array;
    /*
    parent_pid = pid;
    pointer_to_parent_array = pointer_to_array;
    HANDLE hProcess = OpenProcess(PROCESS_VM_READ, FALSE, pid);
    if (hProcess == NULL)
    {
        std::cerr << "Failed to open process." << std::endl;
    }
    char buffer[sizeof(float) * test_array_length];
    SIZE_T bytesRead;
    LPCVOID addressToRead = (LPCVOID)pointer_to_array; // Replace with the desired address
    if (ReadProcessMemory(hProcess, addressToRead, buffer, sizeof(buffer), &bytesRead))
    {
        std::cout << "Read " << bytesRead << " bytes: " << buffer << std::endl;
    }
    else
    {
        std::cerr << "Failed to read memory." << std::endl;
    }


    float recieved;
    memcpy(&recieved, &buffer, sizeof(recieved));
    std::cout << recieved << "\n";
    // Close the process handle
    CloseHandle(hProcess);
    */
}



extern "C" __declspec(dllexport) uintptr_t get_array_pointer()
{
    //std::cout << "rn:  " << test_array[0] << "\n";
    return reinterpret_cast<uintptr_t>(&test_array[0]);
}


char buffer[sizeof(float) * test_array_length];
extern "C" __declspec(dllexport) void get_array_child(float array_out[])
{
    get_parent_array(buffer, sizeof(buffer));
    memcpy(array_out, buffer, test_array_length * sizeof(float));
}




extern "C" __declspec(dllexport) void get_array(float array_out[])
{
    memcpy(array_out, test_array, test_array_length * sizeof(float));
}

extern "C" __declspec(dllexport) void set_array(float array_in[])
{
    memcpy(test_array, array_in, test_array_length * sizeof(float));
}
