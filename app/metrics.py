from prometheus_client import Counter, Histogram

TASK_SUBMITTED = Counter("tasks_submitted_total", "Total tasks submitted")
TASK_SUCCEEDED = Counter("tasks_succeeded_total", "Total tasks succeeded")
TASK_FAILED = Counter("tasks_failed_total", "Total tasks failed")
HTTP_LATENCY = Histogram("http_request_latency_seconds", "HTTP request latency", ["path", "method"])
