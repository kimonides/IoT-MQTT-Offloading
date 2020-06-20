#include <unistd.h>
#include <stdlib.h>

int main(int argc,char* argv[])
{
    sleep(2000);
    return atoi(argv[1])*atoi(argv[2]);
}