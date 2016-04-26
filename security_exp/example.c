#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <openssl/evp.h>

int hash_table[16777216];
char buffer[50];
char hash_value[100];
long long count = 0;

int hex2int(char* hex)
{
  int i;
  int sum = 0;
  for (i = 0; i < strlen(hex); i+=2)
    sum *= 16;
    sum += 16 * (hex[i] - '0') + (hex[i+1] - '0');
  return sum;
}

void gen_string()
{
  srand(count++);
  sprintf(buffer, "%d", rand());
}

int main(int argc, char const *argv[])
{

  int one_way_flag = 0, co_free_flag = 0;
  clock_t start = clock();
  clock_t one_end, co_end;

  memset(hash_table, 0, sizeof(int) * 16777216);

  EVP_MD_CTX *mdctx;
  const EVP_MD *md;

  unsigned char md_value[EVP_MAX_MD_SIZE];
  int md_len, i;

  OpenSSL_add_all_digests();

  if(!argv[1]) {
    printf("Usage: mdtest hash_value\n");
    exit(1);
  }

  md = EVP_get_digestbyname(argv[1]);

  if(!md) {
    printf("Unknown message digest %s\n", argv[1]);
    exit(1);
  }

  char* search_value = argv[2];

  while(1){
    if (co_free_flag && one_way_flag) break;

    mdctx = EVP_MD_CTX_create();
    EVP_DigestInit_ex(mdctx, md, NULL);
    gen_string();
    EVP_DigestUpdate(mdctx, buffer, strlen(buffer));
    EVP_DigestFinal_ex(mdctx, md_value, &md_len);
    EVP_MD_CTX_destroy(mdctx);

    sprintf(hash_value, "%02x%02x%02x", md_value[0], md_value[1], md_value[2]);

    int idx = hex2int(hash_value);
    hash_table[idx]++;
    if (!co_free_flag && hash_table[idx] > 1)
    {
      co_free_flag = 1;
      co_end = clock();
      printf("Collision Found\ndelta time: %d\n", co_end - start);
    }

    if (0 == strcmp(search_value, hash_value)){
      one_way_flag = 1;
      time(&one_end);
      printf("Content Found. The content is %s\ndelta time: %d\n", buffer, one_end - start);
      break;
    }
  }
  /* Call this once before exit. */
  EVP_cleanup();
  exit(0);
}
