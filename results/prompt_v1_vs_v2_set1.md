# Prompt v1 versus v2 on set 1

| Model | Prompt | Single gate pass | Strict gate pass | SYNTAX_ERROR | MISSED_SHOWN | TOO_NARROW | NOISY | padded_values | duplicate_keys |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| qwen2.5-coder:7b | v1 | 10 | 10 | 2 | 0 | 0 | 0 | 7 | 1 |
| qwen2.5-coder:7b | v2 | 12 | 12 | 0 | 0 | 0 | 0 | 1 | 0 |
| qwen2.5-coder:14b | v1 | 11 | 11 | 0 | 1 | 0 | 0 | 6 | 0 |
| qwen2.5-coder:14b | v2 | 8 | 8 | 4 | 0 | 0 | 0 | 0 | 0 |
