# -*- coding: utf-8 -*-

import sys, meistertask

# create MeisterTaskButler object
mtb = meistertask.mtb("ENTER-YOUR-ACCESS-TOKEN-HERE", "London")

# assign currently unassigned tasks to "John Doe"
mtb.assignUnassignedTasksToPerson("YOUR-PROJECT", "John", "Doe")

# mark tasks in section "done" as completed
mtb.markTasksCompleted("YOUR-PROJECT", "done")

# archive completed tasks
mtb.archiveCompletedTasks("YOUR-PROJECT")

# create new task
mtb.createTask("YOUR-PROJECT", "YOUR-SECTION", "YOUR-TASK-NAME", "YOUR-TASK-NOTE", "YOUR-ASSIGNEE-FIRSTNAME", "YOUR-ASSIGNEE-LASTNAME")

# create new task with due date
mtb.createTask("YOUR-PROJECT", "YOUR-SECTION", "YOUR-TASK-NAME", "YOUR-TASK-NOTE", "YOUR-ASSIGNEE-FIRSTNAME", "YOUR-ASSIGNEE-LASTNAME", "2018-12-24 10:30")

# create new task with relative due date "in 8 hours"
mtb.createTaskRelativeDueDate("YOUR-PROJECT", "YOUR-SECTION", "YOUR-TASK-NAME", "YOUR-TASK-NOTE", "YOUR-ASSIGNEE-FIRSTNAME", "YOUR-ASSIGNEE-LASTNAME", "hours", 8)
