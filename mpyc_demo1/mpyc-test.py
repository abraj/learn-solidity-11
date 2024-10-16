import numpy as np
from mpyc.runtime import mpc

secint = mpc.SecInt(32)
secfld = mpc.SecFld(2**8)
f256 = secfld.field

async def main():
  async with mpc:

    #1
    x = secint(3)
    y = secint(5)
    z = x * y
    print(z)
    print(await mpc.output(z))  # 15

    # #2
    # a = secfld(2)
    # b = a + 1
    # print(b)
    # print(await mpc.output(b))  # x+1

    # #3
    # my_age = int(input('Enter your age: '))
    # our_ages = mpc.input(secint(my_age))
    # print(our_ages)
    # print(await mpc.output(our_ages))  # [12, 21]

    # #4
    # random_value = mpc.random.randint(secint, 0, 100)
    # print(random_value)
    # print(await mpc.output(random_value)) # 57

    # #5
    # print(secint.field.modulus)  # 18446744073709551427
    # print(secfld.field.modulus)  # x^8+x^4+x^3+x+1
    # print(int(secfld.field.modulus))  # 283

    # #6.1
    # a = secint.field.array([2, 3])
    # print(a)  # [2 3]
    # print(a[1], type(a[1]))  # 3 <class 'mpyc.finfields.GF(18446744073709551427)'>
    # print(secint.array(a))                 # `ArraySecInt32`
    # print(secint.array(np.array([2, 3])))  # `ArraySecInt32`
    # # print(secint.array([2, 3]))          # Error!

    # #6.2
    # a = secfld.field.array([2, 3])
    # print(a)  # [x x+1]
    # print(a[1], type(a[1]))  # x+1 <class 'mpyc.finfields.GF(2^8)'>
    # print(secfld.array(a))                 # `ArraySecFld8(GF(2^8))`
    # print(secfld.array(np.array([2, 3])))  # `ArraySecFld8(GF(2^8))`
    # # print(secint.array([2, 3]))          # Error!

    # #7
    # x = secint(10)
    # a = secint(5)
    # print(x > a)
    # print(await mpc.output(x > a))  # 1

    # #8
    # x = secint(3)
    # y = 1 / x
    # print(y)
    # print(await mpc.output(y))  # -6148914691236517142
    # print(x * y)
    # print(await mpc.output(x * y))  # 1

    # #9
    # x = secint(3)
    # y = mpc.scalar_mul(x, [1, 2, 3])
    # print(y)
    # print(await mpc.output(y))  # [3, 6, 9]

    # #10 [Ref: https://github.com/lschoe/mpyc/discussions/100]
    # a = secint.array(np.array([1, 2, 3]))
    # b = secint.array(np.array([4, 5, 6]))
    # y = a + b
    # print(y)
    # print(y.shape)  # (3,)
    # print(await mpc.output(y))  # [5 7 9] 
    # z = np.concatenate((a, b))
    # print(z)
    # print(z.shape)  # (6,)
    # print(await mpc.output(z))  # [1 2 3 4 5 6]

    # #11
    # a = secint.array(np.array([1, 2, 3]))
    # b = secint.array(np.array([4, 5, 6]))
    # # z = mpc.np_concatenate((a, b))
    # z = np.concatenate((a, b))
    # print(z)
    # print(await mpc.output(z))  # [1 2 3 4 5 6]
    # # z = mpc.np_reshape(z, (2, 3))
    # z = np.reshape(z, (2, 3))
    # print(await mpc.output(z))  # [[1 2 3]
    #                             #  [4 5 6]]
    # # z = mpc.np_transpose(z)
    # # z = z.T
    # z = np.transpose(z)
    # print(z)
    # print(await mpc.output(z))  # [[1 4]
    #                             #  [2 5]
    #                             #  [3 6]]
    # print(z.shape)  # (3, 2)

if __name__ == "__main__":
  mpc.run(main())
