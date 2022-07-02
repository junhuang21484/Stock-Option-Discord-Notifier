# Discord Stock Notifier

This is a discord bot that I created through the use of Hikari and TD 
Ameritrade Api. Now you do not have to be trading on TD Ameritrade in 
order for this bot to work, however, you do need to have a TD Ameritrade
developer account in order to properly set up this bot.

The main function of this bot is that it can help you monitor the stock/option
price of a Ticker/Contract and when the price goes over or under a price 
target that you have set it will notify you.

The main purpose of me creating this bot is to experience the new Discord
features, and to have a taste of this in development library (Hikari).

___

## Setting Up
Here are the steps that you need to do beforehand in order for the bot to
function properly:

1. Create a TD Ameritrade Developer account, then create an app and obtain 
an API key from the app. Click [here](https://developer.tdameritrade.com/content/getting-started) for how to do.
2. Head over to [Discord Developer Portal](https://discord.com/developers/applications)
and create a new APP, and get the token of the bot
3. Invite the bot to your desire server, and you need to mark the field
`bot` and `applications.commands` in the scope section when inviting the bot
4. Get the server id of the bot that you invited to
5. Create a webhook of where you want the notification been sent to. (This 
step is a must for now, since channel notification is not out yet).
6. Go to `setting.json` and modify the following:
   1. Change `api_key` under `TD_SETTING` to the api key you obtain in step 1
   2. Change `token` under `DISCORD_SETTING` to the bot token you obtain in step 2
   3. Change `webhook` under `DISCORD_SETTING` to the webhook you created in step 5
   4. Add the server id that you obtain in step 4 to the list of `default_guilds` under `DISCORD_SETTING`

After this you will be all setup and can start the bot

___
## Example

Coming soon...
___

## To-Do List
* [] Better documentations
* [] Push an update for channel notifications
* [] Better help command
* [] Loggings
* [] More interactions and features

Now please keep in mind that this project was built for me to get a taste of
Hikari and the new Discord features. Please do no expect updates often, and
if Hikari all of sudden have major changes (they are still in dev) I will
try my best to update.