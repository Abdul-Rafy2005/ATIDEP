# Registry experiment summary

Prompt: registry_v1 | Logsource: registry_set | Techniques: 8 | Temperature: 0.0

| Model | Strict pass | Single pass | Syntax errors | Verdicts |
| --- | ---: | ---: | ---: | --- |
| qwen2.5-coder:14b | 4/8 | 5/8 | 0 | MISSED_SHOWN=1, NOISY=2, PASS=4, TOO_NARROW=1 |
| qwen2.5-coder:7b | 3/8 | 6/8 | 0 | NOISY=2, PASS=3, TOO_NARROW=3 |
