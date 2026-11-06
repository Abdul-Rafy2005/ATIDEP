# Experiment summary

| Model | Single gate pass | Strict gate pass | Verdict counts | Flags | Seconds/rule |
| --- | ---: | ---: | --- | --- | ---: |
| qwen2.5-coder:7b | 36 | 36 | PASS=36 | padded_values=3 | 4.16 |
| qwen2.5-coder:14b | 26 | 26 | PASS=26, SYNTAX_ERROR=10 | duplicate_keys=2 | 9.87 |
