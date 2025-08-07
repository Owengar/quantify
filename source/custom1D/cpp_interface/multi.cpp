


#include <iostream>
#include <windows.h>
#include <math.h>




const int test_array_length = 1000*4000;


float arrays[10][test_array_length];

int parent_pid;

int* setp_index;
bool* transfer_semaphore;



int main()
{
    for (auto array : arrays)
    {
        for (int i=0; i < test_array_length; i++)
        {
            array[i] = NAN;
        }
    }
    std::cout << "dll_main\n";

    setp_index = new int;
    transfer_semaphore = new bool;

    return 0;
}





extern "C" __declspec(dllexport) void dll_main()
{
    main();
}





void get_parent_array(char buffer[sizeof(float) * test_array_length], SIZE_T buffer_size, uintptr_t pointer_to_array)
{
    HANDLE hProcess = OpenProcess(PROCESS_VM_READ, FALSE, parent_pid);
    if (hProcess == NULL)
    {
        std::cerr << "Failed to open process." << std::endl;
    }
    SIZE_T bytesRead;
    LPCVOID addressToRead = (LPCVOID)pointer_to_array; // Replace with the desired address
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


extern "C" __declspec(dllexport) void setup_parent_pid(int pid)
{
    parent_pid = pid;
}

extern "C" __declspec(dllexport) uintptr_t get_transfer_semaphore_pointer()
{
    return reinterpret_cast<uintptr_t>(transfer_semaphore);
}

extern "C" __declspec(dllexport) uintptr_t get_setp_pointer()
{
    return reinterpret_cast<uintptr_t>(setp_index);
}

extern "C" __declspec(dllexport) uintptr_t get_array_pointer(int index)
{
    //std::cout << "rn:  " << arrays[index][0] << "\n";
    return reinterpret_cast<uintptr_t>(&arrays[index][0]);
}


char buffer[sizeof(float) * test_array_length];
extern "C" __declspec(dllexport) void get_array_child(float array_out[], uintptr_t pointer_to_array)
{
    get_parent_array(buffer, sizeof(buffer), pointer_to_array);
    memcpy(array_out, buffer, test_array_length * sizeof(float));
}




extern "C" __declspec(dllexport) void get_array(float array_out[], int index)
{
    memcpy(array_out, arrays[index], test_array_length * sizeof(float));
}

extern "C" __declspec(dllexport) void set_array(float array_in[], int index)
{
    memcpy(arrays[index], array_in, test_array_length * sizeof(float));
}

extern "C" __declspec(dllexport) void set_setp_index(int set_to)
{
    
    //std::cout << "setting to: " << set_to << "\n";
    memmove(setp_index, &set_to, sizeof(set_to));
}

extern "C" __declspec(dllexport) int get_setp_index(uintptr_t address)
{
    int recieve_buffer[1];
    HANDLE hProcess = OpenProcess(PROCESS_VM_READ, FALSE, parent_pid);
    if (hProcess == NULL)
    {
        std::cerr << "Failed to open process." << std::endl;
    }
    SIZE_T bytesRead;
    LPCVOID addressToRead = (LPCVOID)address; // Replace with the desired address
    if (ReadProcessMemory(hProcess, addressToRead, recieve_buffer, sizeof(recieve_buffer), &bytesRead))
    {
        //std::cout << "Read " << bytesRead << " bytes: " << buffer << std::endl;
    }
    else
    {
        std::cerr << "Failed to read memory." << std::endl;
    }
    CloseHandle(hProcess);



    //std::cout << "returning: " << recieve_buffer[0] << "\n";
    return recieve_buffer[0];
}

extern "C" __declspec(dllexport) void set_transfer_semaphore(bool set_to)
{
    memmove(transfer_semaphore, &set_to, sizeof(set_to));
}

extern "C" __declspec(dllexport) bool get_transfer_semaphore(uintptr_t address)
{
    bool recieve_buffer[1];
    HANDLE hProcess = OpenProcess(PROCESS_VM_READ, FALSE, parent_pid);
    if (hProcess == NULL)
    {
        std::cerr << "Failed to open process." << std::endl;
    }
    SIZE_T bytesRead;
    LPCVOID addressToRead = (LPCVOID)address; // Replace with the desired address
    if (ReadProcessMemory(hProcess, addressToRead, recieve_buffer, sizeof(recieve_buffer), &bytesRead))
    {
        //std::cout << "Read " << bytesRead << " bytes: " << buffer << std::endl;
    }
    else
    {
        std::cerr << "Failed to read memory." << std::endl;
    }
    CloseHandle(hProcess);



    //std::cout << "returning: " << recieve_buffer[0] << "\n";
    return recieve_buffer[0];
}