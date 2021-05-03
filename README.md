# Home electricity monitoring system

A small system to monitor electricity at home while sitting far far away. This system messages me on Telegram whenever there's a power cut at my home and whenever the power comes back. 


**Why did I do this?**  

At times, I come home after a grueling journey of over an hour in bus only to open the doors of my home and find a power cutoff at home. In India, this is not so rare. While most societies nowadays have power backup, my small 1BHK does not. 


# How it works 

1. A spare phone kept at home is connected to Wi-Fi at home.
2. This spare phone has Tasker app installed.
3. Every 2 minutes, tasker is used to check for internet connection. If it is able to find internet, it makes an API call to this system. 
4. The API call compares the time this API call came with the time the last API call had come up. If the difference seems high, it means power cut had happened and now power has restored. So, we alert on Telegram.
5. Meanwhile, every single minute, a process checks if it's been more than 2 minutes and we haven't received a new API call from phone. If so, it alerts via telegram that power cut has happened.

The whole telegram alert thing happens via telegram bots. [You can easily build a telegram bot](https://www.reddit.com/r/Telegram/comments/4eqie7/howto_send_messages_to_telegram_channel_with/).

This repository is heroku compatible and the API and the cron bit is implemented as part of this app. Critical files to look at are : `app.py`, `util.py`, and  `clock.py`. 

You can produce a fork of this repo and heroku will automatically understand how to deploy it.

More detailed documentation coming soon.

# How to setup for yourself?

You'll need : 
* A spare phone, or some device where you can either install tasker, or run a program. This device has to have its own battery so it should survive most power cuts.
* Telegram app

# Todo 

* add about how to restart wifi
* write a blog post and add about that blog post as well
* attach tasker backup.xml and tasker tasks n events for this
* add request authentication authorization of some basic kind so nobody can hit ur apis just like that.