# Experiment summary

| Model | Single gate pass | Strict gate pass | Verdict counts | Flags | Seconds/rule |
| --- | ---: | ---: | --- | --- | ---: |
| qwen2.5-coder:14b | 54 | 47 | MISSED_SHOWN=6, PASS=47, TOO_NARROW=7 | padded_values=37 | 5.12 |
| qwen2.5-coder:7b | 56 | 35 | MISSED_SHOWN=3, PASS=35, SYNTAX_ERROR=1, TOO_NARROW=21 | duplicate_keys=6, padded_values=51 | 3.69 |
