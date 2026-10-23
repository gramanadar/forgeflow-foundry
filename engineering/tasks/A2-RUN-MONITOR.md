# A2 Run Monitor Task

Implement a monitor using Cursor's documented v1 Get A Run endpoint. Confirm current endpoint path and response schema against official OpenAPI before coding. Persist agent/run IDs, distinguish running/success/failure, reconcile PR URL and issue labels, and emit alerts for stuck runs. Unit-test 200, 401, 429, 5xx, malformed JSON, terminal error and timeout. Never re-launch a new agent when state is ambiguous.
