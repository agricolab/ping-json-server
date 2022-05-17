#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>

#define PortNumber 1234
#define MaxConnects 8
#define BuffSize 256
#define ConversationLen 3
#define Host "localhost"

void report(const char *msg, int terminate)
{
    perror(msg);
    if (terminate)
        exit(-1); /* failure */
}

int main()
{
    int sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock < 0)
        report("socket", 1); /* terminate */
    struct linger lin;
    lin.l_onoff = 0;
    lin.l_linger = 0;
    setsockopt(sock, SOL_SOCKET, SO_LINGER, (const char *)&lin, sizeof(int));
    if (setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &(int){1}, sizeof(int)) < 0)
        perror("setsockopt(SO_REUSEADDR) failed");
    /* bind the server's local address in memory */
    struct sockaddr_in saddr;
    memset(&saddr, 0, sizeof(saddr));          /* clear the bytes */
    saddr.sin_family = AF_INET;                /* versus AF_LOCAL */
    saddr.sin_addr.s_addr = htonl(INADDR_ANY); /* host-to-network endian */
    saddr.sin_port = htons(PortNumber);        /* for listening */

    if (bind(sock, (struct sockaddr *)&saddr, sizeof(saddr)) < 0)
        report("bind", 1); /* terminate */

    /* listen to the socket */
    if (listen(sock, MaxConnects) < 0) /* listen for clients, up to MaxConnects */
        report("listen", 1);           /* terminate */

    fprintf(stderr, "Listening on port %i for clients...\n", PortNumber);
    /* a server traditionally listens indefinitely */
    while (1)
    {
        struct sockaddr_in caddr; /* client address */
        int len = sizeof(caddr);  /* address length could change */

        int client_sock = accept(sock, (struct sockaddr *)&caddr, &len); /* accept blocks */
        if (client_sock < 0)
        {
            report("accept", 0); /* don't terminated, though there's a problem */
            continue;
        }

        /* read from client */
        int i;
        for (i = 0; i < ConversationLen; i++)
        {
            char buffer[BuffSize + 1];
            memset(buffer, '\0', sizeof(buffer));
            int count = read(client_sock, buffer, sizeof(buffer));
            if (count > 0)
            {
                puts(buffer);
                write(client_sock, buffer, sizeof(buffer)); /* echo as confirmation */
                if (strcmp(buffer, "{\"cmd\":\"poison-pill\"}") == 0)
                {
                    puts("Shutting down");
                    close(client_sock);
                    exit(0);
                }
            }
        }
        close(client_sock); /* break connection */
    }                       /* while(1) */
    return 0;
}
