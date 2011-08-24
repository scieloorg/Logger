#include "stdio.h"
#include "stdlib.h"
#include "string.h"

// for microsoft PC little endian compilers
// should compile with unix compilers with modifications
// Released under GNU license - Copyright, 2007.  Seenu S. Reddi, ReddiSS@aol.com

typedef struct link {
  unsigned int minIP;
  unsigned int maxIP;
  char CountryCode[4];
  struct link *nextLink;
} LINK;

LINK links[256*256];
char *memallocs[40000]; // sufficient now, increase if there is an error.
unsigned int memallocPtr = 0;

void InitDataBase(FILE *fp)
{
  char line[256];
  unsigned int IP, minIP, maxIP;
  unsigned char IPB[4];
  LINK *findLink, *prevLink;
  int i, j, ptr;
  char CountryCode[4];

  // init to 0's
  memset((char *) links, 0, 256*256);
  memallocPtr = 0;

  while (fgets(line, 256, fp) != NULL) {
    if (line[0] != '"')
      continue;

    IP = atoi(line + 1);
    minIP = IP;

    // find , for maxIP
    i = 0;
    while (line[i] != ',')
      i++;
    i += 2;
    maxIP = atoi(line + i);

    // find the country
    for (j = 0; j < 3; j++) {
      while (line[i] != ',')
        i++;
      i += 2;
    }

    // save the country code
    strncpy(CountryCode, line + i, 2);
    CountryCode[2] = 0;

    * (unsigned int *) IPB = IP;
    findLink = (LINK *) &links[IP >> 16];
    if (findLink->minIP == 0 && findLink->maxIP == 0) { // first link
      findLink->minIP = minIP;
      findLink->maxIP = maxIP;
      strcpy(findLink->CountryCode, CountryCode);
      findLink->nextLink = NULL;
    } else {
      while (findLink->nextLink != NULL) {
        findLink = findLink->nextLink;
      }
      prevLink = findLink;
      findLink = findLink->nextLink = (LINK *) malloc(sizeof(LINK));
      memallocs[memallocPtr] = (char *) findLink;
      findLink->minIP = minIP;
      findLink->maxIP = maxIP;
      strcpy(findLink->CountryCode, CountryCode);
      findLink->nextLink = NULL;

      // see if links can be coalesced
      if (((prevLink->maxIP + 1) == findLink->minIP) && strcmp(prevLink->CountryCode, findLink->CountryCode) == 0) {
        prevLink->maxIP = findLink->maxIP;
        prevLink->nextLink = NULL;
        free(memallocs[memallocPtr]);
      } else {
        memallocPtr++;
        if (memallocPtr >= 40000) {
          //printf("Increase the allocation of memallocs !\n");
          return;
        }
      }
    }
  }
}

void CloseDataBase()
{
  int i;

  // unallocate memory
  for (i = 0; i < memallocPtr; i++)
    free(memallocs[i]);
}

// need the data base IpToCountry.csv from http://software77.net/cgi-bin/ip-country/geo-ip.pl
// will work under Microsoft Windows environment
void main(int argc, char *argv[])
{
  FILE *fp;
  unsigned int IP, minIP, maxIP, maxDiff, tIP;
  unsigned char IPB[4];
  LINK *findLink;
  char line[256];
  int i, j, ptr;
  
  fp = fopen("IpToCountry.csv", "r");
    
  if (!fp) {
    printf("Cannot find the IpToCountry.csv CSV file !\n");
    return;
  }

  InitDataBase(fp);
  fclose(fp);
  
  if(argv[1]){
	strncpy(line, argv[1], 256);
  }
  
  if (strchr(line, '.') != NULL) {
    IPB[3] = atoi(line);
 
    ptr = 0;
    for (i = 2; i >= 0; i--) {
      while (line[ptr] != '.')
        ptr++;
      ptr++;
      IPB[i] = atoi(line + ptr);
    }
    IP = * (unsigned int *) IPB;
  } else {
    IP = atoi(line);
    * (unsigned int *) IPB = IP;
  }

  findLink = (LINK *) &links[IP >> 16];
  
  if(argv[2]){
	  if ((strcmp(argv[2],"-p") == 0)){
		  printf("%d.%d.%d.%d|", IPB[3], IPB[2], IPB[1], IPB[0]);
	  }
  }  
  
  i = 0;
  do {
    if (IP >= findLink->minIP && IP <= findLink->maxIP) {
      printf("%s\n", findLink->CountryCode);
      i = 1;
      break;
    }
    findLink = findLink->nextLink;
  } while (findLink != NULL);

  if (i == 0) { // try the bigger blocks
    tIP = (IP >> 16) & 0x0FF00;
    for (j = 0; j < 256; j++) {
      findLink = (LINK *) &links[tIP + j];
      if (IP >= findLink->minIP && IP <= findLink->maxIP) {
        printf("%s\n", findLink->CountryCode);
        i = 1;
        break;
      }
    }
  }

  if (i == 0) {
    printf("Unassigned IP\n");
  }
  
  // clean up - free memory allocated
  CloseDataBase();
}
