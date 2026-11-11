import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from llm import run_experiment


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps({"response": "title: test", "eval_count": 1,
                           "eval_duration": 1_000_000_000}).encode()


def test_options_reach_request_body():
    seen = {}

    def fake_urlopen(request, timeout):
        seen.update(json.loads(request.data))
        return FakeResponse()

    original = run_experiment.urllib.request.urlopen
    run_experiment.urllib.request.urlopen = fake_urlopen
    try:
        run_experiment.ask("http://test", "model", "prompt", 801, 0.2, 103)
    finally:
        run_experiment.urllib.request.urlopen = original

    assert seen["options"]["temperature"] == 0.2
    assert seen["options"]["seed"] == 103
    assert seen["options"]["num_predict"] == 801


def test_repair_hint_is_opt_in():
    requests = []

    def fake_urlopen(request, timeout):
        requests.append(json.loads(request.data)["prompt"])
        return FakeResponse()

    original = run_experiment.urllib.request.urlopen
    run_experiment.urllib.request.urlopen = fake_urlopen
    hint = ("A list item in your rule is a key and value pair, but every list item must be plain text. "
            "Modifiers such as windash belong in the key name (for example CommandLine|contains|windash|all:), "
            "never as a list item. Write the whole rule again.")
    try:
        p1 = run_experiment.build_repair_prompt("p", "r", "Unsupported type: <class 'dict'>", False)
        p2 = run_experiment.build_repair_prompt("p", "r", "other syntax error", True)
        p3 = run_experiment.build_repair_prompt("p", "r", "Unsupported type: <class 'dict'>", True)
        run_experiment.ask("http://test", "model", p1, 801, 0, None)
        run_experiment.ask("http://test", "model", p2, 801, 0, None)
        run_experiment.ask("http://test", "model", p3, 801, 0, None)
    finally:
        run_experiment.urllib.request.urlopen = original

    assert hint not in requests[0]
    assert hint not in requests[1]
    assert hint in requests[2]


def test_prompt_v2_1_accepted():
    parser = run_experiment.build_parser()
    args = parser.parse_args(["--set", "1", "--prompt", "v2_1", "--models", "qwen2.5-coder:7b"])
    assert args.prompt == "v2_1"

    from generator.generate import TECHNIQUES
    from llm.compare_models import DESCRIPTIONS
    prompt_text = run_experiment.prompt_for("v2_1", "T1059.001", TECHNIQUES, DESCRIPTIONS)
    assert "CommandLine|contains|windash|all:" in prompt_text
    assert "Example 3" in prompt_text


def test_prompts_v3a_v3b_accepted():
    parser = run_experiment.build_parser()
    args_3a = parser.parse_args(["--set", "1", "--prompt", "v3a", "--models", "qwen2.5-coder:7b"])
    assert args_3a.prompt == "v3a"
    args_3b = parser.parse_args(["--set", "1", "--prompt", "v3b", "--models", "qwen2.5-coder:7b"])
    assert args_3b.prompt == "v3b"

    from generator.generate import TECHNIQUES
    from llm.compare_models import DESCRIPTIONS
    p3a = run_experiment.prompt_for("v3a", "T1059.001", TECHNIQUES, DESCRIPTIONS)
    assert "-type=txt" in p3a
    p3b = run_experiment.prompt_for("v3b", "T1059.001", TECHNIQUES, DESCRIPTIONS)
    assert "# keep:" in p3b


if __name__ == "__main__":
    test_options_reach_request_body()
    test_repair_hint_is_opt_in()
    test_prompt_v2_1_accepted()
    test_prompts_v3a_v3b_accepted()
    print("temperature=0.2 seed=103 reached the mocked request body")
    print("repair hint is opt-in")
    print("prompt v2_1 accepted by run_experiment")
    print("prompts v3a and v3b accepted by run_experiment")