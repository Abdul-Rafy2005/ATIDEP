# File experiment summary

Prompt: file_v1 | Logsource: file_event | Techniques: 8 | Temperature: 0.0

| Model | Strict pass | Single pass | Syntax errors | Verdicts |
| --- | ---: | ---: | ---: | --- |
| qwen2.5-coder:14b | 0/8 | 6/8 | 0 | MISSED_SHOWN=1, NOISY=1, TOO_NARROW=6 |
| qwen2.5-coder:7b | 0/8 | 5/8 | 2 | MISSED_SHOWN=1, SYNTAX_ERROR=2, TOO_NARROW=5 |
