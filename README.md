# MeisterTaskButler

MeisterTask is a wonderful project management tool based on the Kabana approach. To automate it to some degree and still stay within the free **basic bundle** I decided to build MeisterTaskButler.

MTB offers several ways to manage your tasks and projects in an automated way. You can create tasks, assign them to users, mark them as completed once they reach a specific section or archive all the completed tasks.

For recurring management tasks build several scripts an run them via **cron**.

## Examples

Please see **example.py** for example tasks that MeisterTaskButler can do for you. Please note that all those examples use sample values. If you run these without modification **they will not work**.

## Obtain API Access Token

You will need an API Access Token to let MeisterTaskButler handle your tasks and projects. You can obtain one with just a few clicks.

* navigate to https://www.mindmeister.com/api/index
* scroll down to **Personal Access Tokens**
* click "add"
* enable
  * **meistertask** Read and write access to your MeisterTask projects and tasks
* disable all the other options
  * they're not needed for MeisterTaskButler
* click on submit
