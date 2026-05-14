# Task Priority

## ADDED Requirements

### Requirement: Task Priority Parameter
The system SHALL accept a `priority` parameter in `Scheduler.add_task()` with values "high", "medium", or "low". The default value SHALL be "medium".

#### Scenario: Valid Priority Values
- **WHEN** user calls `add_task()` with `priority="high"`
- **THEN** task is created with high priority

#### Scenario: Invalid Priority Value
- **WHEN** user calls `add_task()` with `priority="invalid"`
- **THEN** system raises ValueError

#### Scenario: Default Priority
- **WHEN** user calls `add_task()` without specifying priority
- **THEN** task is created with "medium" priority

### Requirement: Priority-Based Execution Order
The system SHALL execute tasks in priority order: high priority tasks SHALL be executed before medium, and medium before low. Within the same priority level, tasks SHALL be executed in FIFO order.

#### Scenario: High Priority First
- **WHEN** scheduler has high and medium priority tasks ready to run
- **THEN** high priority task executes first

#### Scenario: Same Priority FIFO
- **WHEN** scheduler has two medium priority tasks
- **THEN** the earlier added task executes first

### Requirement: Task Priority Storage
The `Task` object SHALL store the priority value and provide access to it.

#### Scenario: Priority Access
- **WHEN** task is created with priority
- **THEN** task.priority returns the correct value