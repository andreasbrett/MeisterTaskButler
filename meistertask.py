"""
    MeisterTaskButler
    ~~~~~~~~~~~~~~~~~~
    Mini-Framework for MeisterTask to make automizing task management easier
    :copyright: © 2018 Andreas Brett
    :license: GNU General Public License v3.0, see LICENSE for more details
"""

# -*- coding: utf-8 -*-

import urllib, urllib2, json, datetime, smtp


class mtb:


	# ================================================================================================================
	#  CONSTANTS
	# ================================================================================================================
	comment = "**Automated Change** \n * Script: `" + __file__ + "` \n * Method: `%TEXT%`"





	# ================================================================================================================
	#  URIs for different API requests
	# ================================================================================================================
	uriProjects = "https://www.meistertask.com/api/projects"
	uriProjectTasks = "https://www.meistertask.com/api/projects/%ID%/tasks"
	uriProjectSections = "https://www.meistertask.com/api/projects/%ID%/sections"
	uriProjectLabels = "https://www.meistertask.com/api/projects/%ID%/labels"
	uriProjectPersons = "https://www.meistertask.com/api/projects/%ID%/persons"
	uriSectionTasks = "https://www.meistertask.com/api/sections/%ID%/tasks"
	uriTasks = "https://www.meistertask.com/api/tasks"
	uriTask = "https://www.meistertask.com/api/tasks/%ID%"
	uriTaskComments = "https://www.meistertask.com/api/tasks/%ID%/comments"
	uriPerson = "https://www.meistertask.com/api/persons/%ID%"





	# ================================================================================================================
	#  CONSTRUCTOR
	# ================================================================================================================
	def __init__(self, apiAccessToken, location = "Berlin", TelegramBot = None):
		self.apiAccessToken = apiAccessToken
		self.location = location
		self.TelegramBot = TelegramBot



	# ================================================================================================================
	#  BASIC FUNCTIONS
	# ================================================================================================================
	def sendTelegram(self, message):
		if self.TelegramBot:
			self.TelegramBot.sendMessage(message)

	def getLocalTimezoneOffset(self, location):
		request = urllib2.Request("https://timezoneapi.io/api/address/?" + location)
		response = urllib2.urlopen(request).read()
		data = json.loads(response.decode("utf-8"))

		if data["data"]["addresses_found"] < 1:
			return None
		else:
			return data["data"]["addresses"][0]["datetime"]["offset_gmt"]

	def makeApiRequest(self, apiUri, queryParams = None, bodyParams = None, bodyParamsPost = None):
		# build request if queryParams are present
		if queryParams:
			uri = apiUri + "?" + urllib.urlencode(queryParams)
			request = urllib2.Request(uri, headers={"Authorization" : "Bearer " + self.apiAccessToken})
		else:
			# build request if bodyParams are present
			if bodyParams:
				request = urllib2.Request(apiUri, headers={"Authorization" : "Bearer " + self.apiAccessToken}, data=urllib.urlencode(bodyParams))
				request.get_method = lambda: "PUT"
			else:
				# build request if bodyParamsPost are present
				if bodyParamsPost:
					request = urllib2.Request(apiUri, headers={"Authorization" : "Bearer " + self.apiAccessToken}, data=urllib.urlencode(bodyParamsPost))
				# build request if none of them are present
				else:
					request = urllib2.Request(apiUri, headers={"Authorization" : "Bearer " + self.apiAccessToken})

		# fetch response
		response = urllib2.urlopen(request).read()
		
		# return json data
		return json.loads(response.decode("utf-8"))

	def saveTimestampUTC(self, timestamp, file):
		try:
			f = open(file, "w")
			f.write(datetime.datetime.strftime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ"))
			f.close()
			return True
		except:
			return False

	def loadTimestampUTC(self, file):
		try:
			f = open(file, "r")
			return datetime.datetime.strptime(f.read(), "%Y-%m-%dT%H:%M:%S.%fZ")
		except:
			return datetime.datetime(1970, 1, 1)

	def getLastUpdateUTC(self):
		tasks = self.makeApiRequest(mtb.uriTasks)
		lastUpdate = datetime.datetime(1970, 1, 1)
		for task in tasks:
			dateTaskUpdated = datetime.datetime.strptime(task["updated_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
			if dateTaskUpdated > lastUpdate:
				lastUpdate = dateTaskUpdated
		return lastUpdate

	def getProjectsList(self):
		projects = self.makeApiRequest(mtb.uriProjects, {"status": "active"})
		result = []
		for project in projects:
			result.append(project["name"])
		return result
		
	def getProject(self, projectName):
		projects = self.makeApiRequest(mtb.uriProjects, {"status": "active"})
		for project in projects:
			if project["name"] == projectName:
				return project
				break
		return None

	def getProjectSections(self, projectId):
		return self.makeApiRequest(mtb.uriProjectSections.replace("%ID%", str(projectId)), {"status":"active"})

	def getProjectSection(self, projectId, sectionName):
		sections = self.getProjectSections(projectId)
		for section in sections:
			if section["name"] == sectionName:
				return section
				break
		return None
		
	def getProjectLabels(self, projectId):
		return self.makeApiRequest(mtb.uriProjectLabels.replace("%ID%", str(projectId)))

	def getProjectLabel(self, projectId, labelName):
		labels = self.getProjectLabels(projectId)
		for label in labels:
			if label["name"] == labelName:
				return label
				break
		return None

	def getProjectPersons(self, projectId):
		return self.makeApiRequest(mtb.uriProjectPersons.replace("%ID%", str(projectId)))

	def getProjectPerson(self, projectId, firstname, lastname):
		persons = self.getProjectPersons(projectId)
		for person in persons:
			if person["firstname"].lower() == firstname.lower() and person["lastname"].lower() == lastname.lower():
				return person
				break
		return None

	def getUnassignedTasks(self, projectName):
		project = self.getProject(projectName)
		if project is None:
			print "Could not find project '" + projectName + "'"
		else:
			# fetch all open tasks from the project we just found
			openTasks = self.makeApiRequest(mtb.uriProjectTasks.replace("%ID%", str(project["id"])), {"status":"open"})
			if openTasks is None:
				print "There are no open tasks in '" + projectName + "'"
			else:
				# define result
				result = []
				
				# iterate over all tasks
				for openTask in openTasks:
					# only use tasks that are unassigned
					if openTask["assigned_to_id"] is None:
						result.append(openTask)

				return result
		return None
	
	def getIdleTasks(self, projectName, idleUnit = "months", idleValue = 1):
		project = self.getProject(projectName)
		if project is None:
			print "Could not find project '" + projectName + "'"
		else:
			# fetch all open tasks from the project we just found
			openTasks = self.makeApiRequest(mtb.uriProjectTasks.replace("%ID%", str(project["id"])), {"status":"open"})
			if openTasks is None:
				print "There are no open tasks in '" + projectName + "'"
			else:
				# define result
				result = []
				
				# calculate idle date
				dateIdleBorder = datetime.datetime.now() - datetime.timedelta(**{idleUnit:idleValue})
				
				# iterate over all tasks
				for openTask in openTasks:
					# only use tasks that are idle for a specific amount of time
					dateTaskUpdated = datetime.datetime.strptime(openTask["updated_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
					if dateTaskUpdated < dateIdleBorder:
						result.append(openTask)

				return result
		return None





	# ================================================================================================================
	#  ADVANCED FUNCTIONS
	# ================================================================================================================
	def assignUnassignedTasksToPerson(self, projectName, personFirstname, personLastname):
		print
		print "[assignUnassignedTasksToPerson] " + projectName + ", " + personFirstname + " " + personLastname
		
		project = self.getProject(projectName)
		if project is None:
			print "Could not find project '" + projectName + "'"
		else:
			# find person
			person = self.getProjectPerson(project["id"], personFirstname, personLastname)
			if person is None:
				print "Could not find person '" + personFirstname + " " + personLastname + "'"
			else:
				# fetch unassigned tasks for project
				unassignedTasks = self.getUnassignedTasks(projectName)
				if unassignedTasks is None:
					print "no unassigned tasks"
				else:
					# iterate over unassigned tasks
					for unassignedTask in unassignedTasks:
						print "Re-assigning task '" + unassignedTask["name"].encode("utf-8") + "'"
						# assign task to person
						result = self.makeApiRequest(mtb.uriTask.replace("%ID%", str(unassignedTask["id"])), None, {"assigned_to_id":str(person["id"])})
						if result:
							# add comment for change
							self.makeApiRequest(mtb.uriTaskComments.replace("%ID%", str(unassignedTask["id"])), None, None, {"text":mtb.comment.replace("%TEXT%", "assignUnassignedTasksToPerson")})
							print " --> SUCCESS"
							self.sendTelegram("[" + projectName + "]\nRe-assigned task '" + unassignedTask["name"] + "' to " + personFirstname + " " + personLastname)
						else:
							print " --> ERROR"
							self.sendTelegram("[" + projectName + "]\nERROR re-assigning task '" + unassignedTask["name"] + "' to " + personFirstname + " " + personLastname)

	def markTasksCompleted(self, projectName, sectionName):
		print
		print "[markTasksCompleted] " + projectName + " / " + sectionName
		
		project = self.getProject(projectName)
		if project is None:
			print "Could not find project '" + projectName + "'"
		else:
			section = self.getProjectSection(project["id"], sectionName)
			if section is None:
				print "Could not find section '" + sectionName + "' in project '" + projectName + "'"
			else:
				# fetch all open tasks from the section we just found
				openTasks = self.makeApiRequest(mtb.uriSectionTasks.replace("%ID%", str(section["id"])), {"status":"open"})
				if openTasks is None:
					print "There are no open tasks in section '" + sectionName + "' of project '" + projectName + "'"
				else:
					# iterate over open tasks
					for openTask in openTasks:
						print "Marking task '" + openTask["name"].encode("utf-8") + "' completed"
						# mark task completed
						result = self.makeApiRequest(mtb.uriTask.replace("%ID%", str(openTask["id"])), None, {"status":"2"})
						if result:
							# add comment for change
							self.makeApiRequest(mtb.uriTaskComments.replace("%ID%", str(openTask["id"])), None, None, {"text":mtb.comment.replace("%TEXT%", "markTasksCompleted")})
							print " --> SUCCESS"
						else:
							print " --> ERROR"
			
	def archiveCompletedTasks(self, projectName, daysSinceLastChange = 14):
		print
		print "[archiveCompletedTasks] " + projectName + ", " + str(daysSinceLastChange) + " days"
		
		# define now and the minimum delta
		now = datetime.datetime.now()
		minDelta = datetime.timedelta(daysSinceLastChange, 0)
		
		project = self.getProject(projectName)
		if project is None:
			print "Could not find project '" + projectName + "'"
		else:
			completedTasks = self.makeApiRequest(mtb.uriProjectTasks.replace("%ID%", str(project["id"])), {"status":"completed"})
			if completedTasks is None:
				print "There are no completed tasks in '" + projectName + "'"
			else:
				# iterate over all tasks
				for completedTask in completedTasks:
					# calculate last change (relative)
					delta = now - datetime.datetime.strptime(completedTask["status_updated_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
					
					# if this has been completed for "long enough"
					if delta > minDelta:
						print "Archiving task '" + completedTask["name"].encode("utf-8") + "'"
						# mark task completed
						result = self.makeApiRequest(mtb.uriTask.replace("%ID%", str(completedTask["id"])), None, {"status":"18"})
						if result:
							# add comment for change
							self.makeApiRequest(mtb.uriTaskComments.replace("%ID%", str(completedTask["id"])), None, None, {"text":mtb.comment.replace("%TEXT%", "archiveCompletedTasks")})
							print " --> SUCCESS"
						else:
							print " --> ERROR"
							
	def createTask(self, projectName, sectionName, taskName, taskNotes = "", taskAssigneeFirstName = "", taskAssigneeLastName = "", taskDue = None, taskDueLocation = None):
		print
		print "[createTask] " + projectName + " / " + sectionName + ", " + taskName + ", " + taskNotes + ", " + taskAssigneeFirstName + " " + taskAssigneeLastName + ", " + str(taskDue)
		
		if taskDueLocation is None:
			taskDueLocation = self.location
		
		project = self.getProject(projectName)
		if project is None:
			print "Could not find project '" + projectName + "'"
		else:
			section = self.getProjectSection(project["id"], sectionName)
			if section is None:
				print "Could not find section '" + sectionName + "' in project '" + projectName + "'"
			else:
				
				# define parameters
				taskParameters = {
					"name": taskName,
					"status": 1,
					"notes": taskNotes
				}
				
				# find assignee
				if taskAssigneeFirstName != "" and taskAssigneeLastName != "":
					person = self.getProjectPerson(project["id"], taskAssigneeFirstName, taskAssigneeLastName)
					if person:
						taskParameters["assigned_to_id"] = person["id"]
					else:
						print "Could not find Assignee '" + taskAssigneeFirstName + " " + taskAssigneeLastName + "'"
				
				# format due date
				if taskDue:
					taskParameters["due"] = taskDue + self.getLocalTimezoneOffset(taskDueLocation)
				
				# add task
				print "Creating task '" + taskName + "'"
				taskCreated = self.makeApiRequest(mtb.uriSectionTasks.replace("%ID%", str(section["id"])), None, None, taskParameters)
				if taskCreated:
					# add comment for change
					self.makeApiRequest(mtb.uriTaskComments.replace("%ID%", str(taskCreated["id"])), None, None, {"text":mtb.comment.replace("%TEXT%", "createTask")})
					print " --> SUCCESS"
					self.sendTelegram("[" + projectName + "]\nCreated task '" + taskName + "' in Section '" + sectionName + "'")
				else:
					print " --> ERROR"
					self.sendTelegram("[" + projectName + "]\nERROR creating task '" + taskName + "' in Section '" + sectionName + "'")
	
	def createTaskRelativeDueDate(self, projectName, sectionName, taskName, taskNotes = "", taskAssigneeFirstName = "", taskAssigneeLastName = "", taskDueUnit = "hours", taskDueValue = 8, taskDueLocation = None):
				
		if taskDueLocation is None:
			taskDueLocation = self.location
		
		# transform relative time to absolute timestamp
		d = datetime.datetime.now() + datetime.timedelta(**{taskDueUnit:taskDueValue})
		taskDue = datetime.datetime.strftime(d, "%Y-%m-%d %H:%M")
		
		# run createTask method with calculated timestamp
		self.createTask(projectName, sectionName, taskName, taskNotes, taskAssigneeFirstName, taskAssigneeLastName, taskDue, taskDueLocation)
	
	def commentOnIdleTasks(self, projectName, idleUnit, idleValue, comment):
		print
		print "[commentOnIdleTasks] " + projectName + ", " + str(idleValue) + " " + idleUnit + ", " + comment

		# fetch unassigned tasks for project
		idleTasks = self.getIdleTasks(projectName, idleUnit, idleValue)
		if idleTasks is None:
			print "no idle tasks"
		else:
			# iterate over unassigned tasks
			for idleTask in idleTasks:
				print "Commenting task '" + idleTask["name"].encode("utf-8") + "'"
				
				# check if there's an assignee
				if idleTask["assigned_to_id"]:
					self.makeApiRequest(mtb.uriTaskComments.replace("%ID%", str(idleTask["id"])), None, None, {"text":mtb.comment.replace("%TEXT%", "commentOnIdleTasks") + "\n\n <person_id>" + str(idleTask["assigned_to_id"]) + "</person_id> " + comment})
				else:
					self.makeApiRequest(mtb.uriTaskComments.replace("%ID%", str(idleTask["id"])), None, None, {"text":mtb.comment.replace("%TEXT%", "commentOnIdleTasks") + "\n\n" + comment})
				
				print " --> SUCCESS"
	
	def notifyAssigneesOnIdleTasks(self, projectName, idleUnit, idleValue, comment, mailFrom, mailSubject):
		print
		print "[notifyAssigneesOnIdleTasks] " + projectName + ", " + str(idleValue) + " " + idleUnit + ", " + comment

		# fetch unassigned tasks for project
		idleTasks = self.getIdleTasks(projectName, idleUnit, idleValue)
		if idleTasks is None:
			print "no idle tasks"
		else:
			# iterate over unassigned tasks
			for idleTask in idleTasks:
				
				# check if there's an assignee
				if idleTask["assigned_to_id"]:
					# fetch assignee
					assignee = self.makeApiRequest(mtb.uriPerson.replace("%ID%", str(idleTask["assigned_to_id"])))
					
					# notify assignee
					print "Notifying assignee '" + assignee["firstname"] + " " + assignee["lastname"] + " <" + assignee["email"] + ">' about task '" + idleTask["name"].encode("utf-8") + "'"
					mailBodyHtml = "<p><b>" + comment + "</b></p><p><a href=""https://www.meistertask.com/app/task/" + idleTask["token"] + " "">" + idleTask["name"].encode("utf-8") + "</a></p>"
					smtp.sendMail({assignee["email"]}, mailFrom, mailSubject, mailBodyHtml)
					
					# add comment for notification mail
					self.makeApiRequest(mtb.uriTaskComments.replace("%ID%", str(idleTask["id"])), None, None, {"text":mtb.comment.replace("%TEXT%", "notifyAssigneesOnIdleTasks")})
					print " --> SUCCESS"
