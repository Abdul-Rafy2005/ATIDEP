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
    try:
        off = run_experiment.build_repair_prompt("p", "r", "bad", False)
        on = run_experiment.build_repair_prompt("p", "r", "bad", True)
        run_experiment.ask("http://test", "model", off, 801, 0, None)
        run_experiment.ask("http://test", "model", on, 801, 0, None)
    finally:
        run_experiment.urllib.request.urlopen = original

    hint = "A value in your rule was read as a YAML mapping or has a quoting problem."
    assert hint not in requests[0]
    assert hint in requests[1]


if __name__ == "__main__":
    test_options_reach_request_body()
    test_repair_hint_is_opt_in()
    print("temperature=0.2 seed=103 reached the mocked request body")
    print("repair hint is opt-in")