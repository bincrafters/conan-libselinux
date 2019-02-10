#include <iostream>
#include <selinux/selinux.h>

int main()
{
    if (is_selinux_enabled())
        std::cout << "SELinux is enabled" << std::endl;
    else
        std::cout << "SELinux is not enabled" << std::endl;
    return 0;
}
