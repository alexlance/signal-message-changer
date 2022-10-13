# signal-message-changer

Alter the message type of the messages in the Signal database


## Signal have made a decision to delete all of your **SMS messages** that reside in Signal...

According to this: https://www.signal.org/blog/sms-removal-android/

*If you do use Signal as your default SMS app on Android, you will need to select a new default SMS app on your phone. **If you want to keep them**, you’ll also need to export your SMS messages from Signal into that new app.*


## Change the message type

This code changes the type of your SMS text messages in Signal, to make them
look more like Signal messages, so that hopefully they won't all get deleted.

Note: future text messages will still need to be sent with a separate SMS app.
But at least your existing messages won't suddenly disappear.

## Caveats

 * Only tested on Docker, Linux and for Android
 * MAKE SURE YOU:
     - backup Signal before you begin
     - have written down the 30 digit backup code
     - still have your phone number for identity verification
     - still remember your numerical Signal Pin


## Instructions

1. Generate a Signal backup file

```
Signal -> Chats -> Backups -> Local Backup
```

2. Transfer that file to your computer, file will be named eg: signal-2022-06-10-17-00-00.backup

3. Download this repo and run:

```
cd signal-message-changer
export SIG_KEY=123451234512345123451234512345
make run
```

4. A new backup file should be generated. Transfer it back to your phone.

5. Delete Signal from your phone (**only if you're 100% confident that you can use your original backup if things don't work!**)

6. Reinstall Signal, it'll ask you if you've got a backup file that you want to restore from. Select your new file.


## Thoughts
* Feel free to shout out with any issues problems in github issues
* Make sure to go and give signalbackup-tools some kudos as they do most of the heavy lifting
