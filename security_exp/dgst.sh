for x in md4 md5 ripemd160 sha sha1 sha224 sha256 sha384 sha512 mdc2
do
	openssl dgst -$x test.txt
done
