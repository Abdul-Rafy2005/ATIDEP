# Sample Sigma Rules for Gate Demonstration

This folder contains four real Sigma detection rules copied directly from saved first-try model outputs in `results/runs/`. They are used to demonstrate how the automated validation gate evaluates rules on synthetic logs.

## Rule Summary Table

| Rule File | Run Folder | Model | Prompt | Set | Technique | Expected Verdict | Description |
|---|---|---|---|---|---|---|---|
| `rule_a_pass.yml` | `20261111_1500_set3_v3b` | `qwen2.5-coder:14b` | `v3b` | 3 | `T1615` | `PASS` | Generalises using windash with separate flag tokens `/z` and `/user`. Passes all gate checks. |
| `rule_b_narrow_padded.yml` | `20261111_1449_set3_v1` | `qwen2.5-coder:7b` | `v1` | 3 | `T1564.004` | `TOO_NARROW` | Overfits by matching padded adjacent tokens `' -b -f '`. Misses the variant where flag order changes. |
| `rule_c_narrow_copy.yml` | `20261111_1449_set3_v1` | `qwen2.5-coder:7b` | `v1` | 3 | `T1220` | `TOO_NARROW` | Copies exact literal XML file path and attacker URL from shown command line. Misses variant with different arguments. |
| `rule_d_syntax_error.yml` | `20261111_1507_set3_v3a` | `qwen2.5-coder:7b` | `v3a` | 3 | `T1529` | `SYNTAX_ERROR` | Writes a key-value mapping `- '/t': '0'` inside a list under `contains|windash|all`. Fails pySigma compilation. |

## Usage

Run `demo/gate_demo.py` against any sample rule:

```powershell
python demo/gate_demo.py --rule demo/sample_rules/rule_a_pass.yml --set 3 --technique T1615
python demo/gate_demo.py --rule demo/sample_rules/rule_b_narrow_padded.yml --set 3 --technique T1564.004
python demo/gate_demo.py --rule demo/sample_rules/rule_c_narrow_copy.yml --set 3 --technique T1220
python demo/gate_demo.py --rule demo/sample_rules/rule_d_syntax_error.yml --set 3 --technique T1529
```

