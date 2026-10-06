# Agent behavior evals

`cases.json` contains machine-readable agent-behavior cases for this skill. `cases.schema.json` publishes a strict Draft 2020-12 JSON Schema for external tooling.

## Why the assertions are structured

The cases use an assertion list instead of free-form expectation strings so a harness can parse the intended checks without an LLM judge. A harness still needs a small adapter that normalizes its own trace/output into this result shape:

```json
{
  "skill_selected": true,
  "phase": 1,
  "behaviors": ["read_only_audit"],
  "actions": [],
  "tool_calls": ["check_project"]
}
```

The normalized fields are:

- `skill_selected`: whether this skill was selected for the task;
- `phase`: active workflow phase, or `null` when not applicable;
- `behaviors`: semantic decisions demonstrated by the agent;
- `actions`: concrete actions attempted/performed;
- `tool_calls`: normalized tool/script names used by the harness.

Each assertion has:

```json
{"field": "actions", "operator": "not_contains", "value": "render"}
```

Supported assertion combinations in schema version 2 are:

- `skill_selected` + `eq` + boolean;
- `phase` + `eq` + integer `1`-`4` or `null`;
- `behaviors`, `actions`, or `tool_calls` + `contains`/`not_contains` + non-empty string.

The schema rejects unsupported field/operator combinations, wrong value types, extra properties, malformed case ids, and mismatched contract metadata.

This makes the cases mechanically interpretable while leaving harness-specific trace parsing in an adapter. Routing, phase discipline, permission reasoning, and render-loop behavior still require an actual agent/model run; the local Python tests only validate the case schema and deterministic tooling.

For every model/configuration, record at minimum: case id, model, tool availability, normalized result, pass/fail assertions, and a short failure note.
