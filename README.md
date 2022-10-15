# signal-message-changer

Alter the message type of the messages in the Signal database. Three modes:

1. Default mode: make all your SMS/MMS messages in Signal, look like Signal messages.
2. --tosms mode: make all your Signal messages look more like SMS/MMS (this *might* help with exporting the entire Signal message store back to Android...)
3. --undo mode: take previous modifications that have been made with signal-message-changer, and undo them


## Change the message type

This code changes the type of your SMS text messages in Signal, to make them
look more like Signal messages, so that hopefully they won't eventually all get deleted.

Note: future text messages will still need to be sent with a separate SMS app.
But at least your existing messages won't suddenly one day disappear if Signal decides
to stop showing (or delete) the old messages.

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
export SIG_FILE=signal-2022-06-10-17-00-00.backup
make run
```

4. A new backup file should be generated named `signal-all-messages.backup`. Transfer it back to your phone.

5. Delete Signal from your phone (**only if you're 100% confident that you can use your original backup if things don't work!**)

6. Reinstall Signal, it'll ask you if you've got a backup file that you want to restore from. Select your new file.


## Thoughts
* Feel free to shout out with any issues problems in github issues
* Make sure to go and give signalbackup-tools some kudos as they do most of the heavy lifting
