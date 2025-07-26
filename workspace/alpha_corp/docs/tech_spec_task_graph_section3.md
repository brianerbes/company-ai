## Dynamic Task Graph - Technical Specification: Section 3 - Data Model

**Database:** PostgreSQL

**Task Entity:**
* `id` (UUID, primary key)
* `name` (varchar(255))
* `status` (enum: CREATED, RUNNING, COMPLETED, FAILED)
* `creation_timestamp` (timestamp)
* `completion_timestamp` (timestamp, nullable)
* `data` (JSONB)

**Dependency Entity:**
* `id` (UUID, primary key)
* `task_id` (UUID, foreign key referencing Task.id)
* `dependency_id` (UUID, foreign key referencing Task.id)
* `type` (enum: PRECEDENCE, EXCLUSION)

**Relationships:**  One-to-many between Task and Dependency (a task can have multiple dependencies).