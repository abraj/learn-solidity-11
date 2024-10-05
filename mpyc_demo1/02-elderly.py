"""MPyC Demo

Run the following commands in separate terminals:

  python 02-elderly.py -M 3 -I0
  python 02-elderly.py -M3 -I1 --no-log
  python 02-elderly.py -M3 -I2 --no-log

In this case, `len(mpc.parties)` is 3.

Get help:
  python -m mpyc -H

MPyC REPL/Get secure types:
  python -m mpyc

Demos:
  https://mpyc.readthedocs.io/en/latest/demos.html
  https://github.com/lschoe/mpyc/tree/master/demos

Docs:
  https://mpyc.readthedocs.io/en/latest/cli.html#command-line
"""

from mpyc.runtime import mpc


async def main():
  secint = mpc.SecInt(16)
  print('==>', mpc.pid, len(mpc.parties), mpc.parties)
  
  await mpc.start()     # connect to all other parties

  my_age = int(input('Enter your age: '))
  our_ages = mpc.input(secint(my_age))

  total_age = sum(our_ages)
  max_age = mpc.max(our_ages)
  m = len(mpc.parties)
  above_avg = mpc.sum(age * m > total_age for age in our_ages)

  print('Average age:', await mpc.output(total_age) / m)
  print('Maximum age:', await mpc.output(max_age))
  print('Number of "elderly":', await mpc.output(above_avg))

  await mpc.shutdown()  # disconnect, but only once all other parties reached this point

if __name__ == '__main__':
  mpc.run(main())
