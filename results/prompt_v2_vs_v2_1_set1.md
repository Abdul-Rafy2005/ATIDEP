# Prompt v2 versus v2.1 on set 1

| Configuration | First-try syntax errors | First-try strict pass out of 36 | Final pass after repair | Seconds per rule |
| --- | ---: | ---: | ---: | ---: |
| qwen 14b v2 (run 20261104_1503) | 10 | 26/36 | 26 | 9.87 |
| qwen 14b v2 plus repair hint (run A) | 10 | 26/36 | 36 | 7.27 |
| qwen 14b v2_1 (run B) | 0 | 36/36 | 36 | 5.25 |
| qwen 7b v2 (run 20261104_1503) | 0 | 36/36 | 36 | 4.16 |
| qwen 7b v2_1 (run B) | 0 | 36/36 | 36 | 3.74 |

Note on Run A: All 10 first-try syntax failures were fixed upon repair and passed the gate, giving 36/36 final passes (29/36 if additionally requiring the set 1 variant log).

## Syntax errors in runs A and B

### Run B (prompt v2_1)
There are 0 syntax errors on first-try and 0 syntax errors on final rules for both qwen 14b and qwen 7b.

### Run A (prompt v2 with repair hint for qwen 14b)
On first try, 10 rules failed with a syntax error because qwen 14b wrote windash as a dictionary list item inside `CommandLine|contains|all:`, producing the pySigma error `Unsupported type: <class 'dict'>`.

Failing first-try lines:
- T1059.001 (repeats 1, 2, 3):
  `CommandLine|contains|all:`
  `- windash: '-nop'`
  `- windash: '-w hidden'`
  `- windash: '-c IEX'`
- T1218.010 (repeats 1, 2, 3):
  `CommandLine|contains|all:`
  `- windash: '-s'`
  `- windash: '-u'`
  `- windash: '-i:http://'`
- T1105 (repeat 2):
  `CommandLine|contains|all:`
  `- windash: '-urlcache'`
  `- windash: '-f'`
- T1003.001 (repeats 1, 2, 3):
  `CommandLine|contains|all:`
  `- windash: '-ma'`

With the repair hint, all 10 rules were re-generated with `CommandLine|contains|windash|all:`. After repair, 0 rules still have a syntax error in Run A.

## qwen 7b v2_1 passes per technique (Run B)

- T1003.001: 3/3
- T1033: 3/3
- T1047: 3/3
- T1053.005: 3/3
- T1059.001: 3/3
- T1105: 3/3
- T1136.001: 3/3
- T1197: 3/3
- T1218.005: 3/3
- T1218.010: 3/3
- T1218.011: 3/3
- T1547.001: 3/3
