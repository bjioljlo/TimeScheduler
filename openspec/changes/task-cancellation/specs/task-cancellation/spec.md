# Task Cancellation

## ADDED Requirements

### Requirement: Task Cancellation API
The system SHALL provide a `cancel_task(task_id)` method in `Scheduler` that attempts to cancel a task. The method SHALL return `True` if cancellation was initiated successfully, `False` otherwise.

#### Scenario: Cancel Pending Task
- **WHEN** user calls `cancel_task()` on a pending task
- **THEN** task is removed from scheduler and method returns `True`

#### Scenario: Cancel Non-existent Task
- **WHEN** user calls `cancel_task()` with invalid task_id
- **THEN** method returns `False`

### Requirement: Task Status Tracking
The `Task` object SHALL maintain a status attribute with values: "pending", "running", "cancelled", "completed".

#### Scenario: Status Transitions
- **WHEN** task is created
- **THEN** status is "pending"
- **WHEN** task starts executing
- **THEN** status changes to "running"
- **WHEN** task is cancelled
- **THEN** status changes to "cancelled"

### Requirement: Cooperative Cancellation
The system SHALL support cooperative cancellation for running tasks using a cancellation token.

#### Scenario: Cancellation Token Access
- **WHEN** task function receives a cancellation token
- **THEN** it can check `token.is_cancelled()` to determine if cancellation was requested

#### Scenario: Graceful Cancellation
- **WHEN** task function checks cancellation and exits early
- **THEN** task status becomes "cancelled" and `on_cancel` callback is triggered

### Requirement: Cancellation Callback
The system SHALL support an optional `on_cancel` callback that is triggered when a task is cancelled.

#### Scenario: Cancel Callback Execution
- **WHEN** task is cancelled
- **THEN** `on_cancel` callback is called with task name