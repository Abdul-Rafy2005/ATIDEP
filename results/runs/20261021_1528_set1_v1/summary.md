# Experiment summary

| Model | Single gate pass | Strict gate pass | Verdict counts | Flags | Seconds/rule |
| --- | ---: | ---: | --- | --- | ---: |
| qwen2.5-coder:7b | 28 | 28 | PASS=28, SYNTAX_ERROR=8 | COPIED=3, duplicate_keys=2, padded_values=18 | 4.53 |
| qwen2.5-coder:14b | 35 | 35 | MISSED_SHOWN=1, PASS=35 | duplicate_keys=1, padded_values=20 | 5.36 |
