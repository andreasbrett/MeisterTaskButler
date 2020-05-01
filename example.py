# -*- coding: utf-8 -*-

import sys, meistertask

# create MeisterTaskButler object
mtb = meistertask.mtb("ENTER-YOUR-ACCESS-TOKEN-HERE", "London")

# create MeisterTaskButler object with TelegramBot support (see https://github.com/andreasbrett/TelegramBot)
#  -> will send some notifications via Telegram
tgb = TelegramBot.tgb("ENTER-YOUR-ACCESS-TOKEN", "ENTER-YOUR-GLOBAL-CHAT-ID-HERE")
mtb_tgb = meistertask.mtb("ENTER-YOUR-ACCESS-TOKEN-HERE", "London", tgb)

# get a list of all active projects and iterate over them
projects = mtb.getProjectsList()
for project in projects:
    print(project)

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

# check for idle tasks and comment on them
mtb.commentOnIdleTasks("YOUR-PROJECT", "months", 2, "Task has been idle for 2 months now. Please check!")

# check for idle tasks and send notification mail to assignee
mtb.notifyAssigneesOnIdleTasks("YOUR-PROJECT", "months", 2, "Found idle task", "MeisterTaskButler <your-email@address.com>", "Found an idle task that has not been updated for 2 months now.")
