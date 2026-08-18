# Persistent Job Queue Contract

The job queue is the durable orchestration boundary between future pipeline steps and workers.

## Job identity

Each job has an immutable UUID and belongs to exactly one project.

## Payload

`payload` is a JSON object. It contains job-specific inputs and remains vendor-neutral. Provider-specific credentials must never be embedded in a job payload.

## Lifecycle

```text
queued → running → succeeded
              └→ queued (retry)
              └→ failed

queued/running → cancelled
```

A worker claims only queued jobs whose `available_at` has arrived.

## Ordering

Eligible jobs are ordered by highest priority first, then oldest creation time for equal priority.

## Concurrency

Claiming uses a SQLite `BEGIN IMMEDIATE` transaction. The selected row is changed from `queued` to `running` in the same transaction, preventing two workers using separate connections from claiming the same job.

## Retry policy

`attempts` increments only when a worker successfully claims a job. A failed job is returned to `queued` while `attempts < max_attempts`. Once the final allowed attempt fails, the job becomes `failed` and receives `finished_at`.

## Terminal operations

- `succeeded`: worker completed the operation and may store a JSON result.
- `failed`: no further automatic retries remain.
- `cancelled`: explicitly stopped before completion.

The queue does not execute jobs itself. Worker execution and pipeline semantics belong to later stages.
