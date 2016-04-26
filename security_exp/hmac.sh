for x in md5 sha1 sha256; do
	openssl dgst -$x -hmac "klsdja;dsljfnvakldsfjcmlkcmlskfcm;lszmfc;l" test.txt
done

for x in md5 sha1 sha256; do
	openssl dgst -$x -hmac "x" test.txt
done
