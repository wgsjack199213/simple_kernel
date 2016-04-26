#-*- coding:utf8 -*-
import hashlib
import binascii
import random

hash_table = {}

def attack(offset=0, preimage='000000'):
    counter = 1
    hash_table = {}

    oneWay = False
    collision = False

    result = []

        
    while(True):
        #n = int('0b110100001100101011011000110110001101111', 2)
        n = counter + offset
        hex_str = '%x' % n
        if len(hex_str) % 2 == 1:
            hex_str = '0' + hex_str
        message = binascii.unhexlify(hex_str)

        m = hashlib.md5()
        m.update(message)
        #print m.hexdigest()

        digest = m.hexdigest()[:6]

        if not collision:
            if hash_table.has_key(digest):
                result.append([counter, hex_str, hash_table[digest], digest])
                collision = True
                print 'Collision!'
            else:
                hash_table[digest] = hex_str

        if not oneWay and int(digest, 16) == preimage:
            result.append([counter, hex_str, digest])
            oneWay = True
            print 'One way!'
            
        if oneWay and collision:
            break

        if counter >= 2 ** 32:
            result = 'Failure'
            break
        counter += 1

    return result

if __name__ == '__main__':
    block_size = 2 ** 24
    num_exp = 10

    for k in range(num_exp):
        preimage = random.randint(0, block_size)
        offset = random.randint(0, block_size)
        print 'preimage:', hex(preimage), 'offset:', offset
        print attack(offset=offset, preimage=preimage)
