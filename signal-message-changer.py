import os
import sys
import sqlite3
import logging
import argparse

parser = argparse.ArgumentParser(description='Update SMS messages to look like native Signal messages OR update Signal messages to look like SMS messages...')

parser.add_argument('args', nargs='*')
parser.add_argument('--undo', '-u', dest='undo', action='store_true', help="Undo mode: revert your message types back to how they were originally")
parser.add_argument('--tosms', '-m', dest='tosms', action='store_true', help="Cheeky mode: convert signal messages to sms (perhaps for export later...)")
parser.add_argument('--verbose', '-v', dest='verbose', action='store_true', help='Make logging more verbose')
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG if args.verbose else logging.INFO)


def run_cmd(cmd):
    logging.info(f"running command: {cmd}")
    r = os.popen(cmd)
    logging.info(r.read())
    rtn = r.close()
    if rtn is not None:
        logging.info(f"command failed: {cmd}")
        sys.exit(rtn)


def print_num_sms():
    q = "select count(*) as tally from message where type in (20, 22, 23, 24, 87, 88) and m_type = 0"
    cursor.execute(q)
    (tally,) = cursor.fetchone()
    logging.info(f"Total num SMS messages: {tally}")


def print_num_signal():
    q = "select count(*) as tally from message where type in (10485780, 10485783, 10485784) and m_type = 0"
    cursor.execute(q)
    (tally,) = cursor.fetchone()
    logging.info(f"Total number Signal messages: {tally}")


def print_num_mms():
    q = "select count(*) as tally from message where type in (20, 22, 23, 24, 87, 88) and m_type in (128, 130, 132)"
    cursor.execute(q)
    (tally,) = cursor.fetchone()
    logging.info(f"Total num MMS messages: {tally}")


def print_num_signal_mms():
    q = "select count(*) as tally from message where type in (10485780, 10485783, 10485784) and m_type in (128, 130, 132)"
    cursor.execute(q)
    (tally,) = cursor.fetchone()
    logging.info(f"Total number Signal Multimedia messages: {tally}")


def undo_changes_to_sms():
    q = '''update message set
             type = original_message_type,
             original_message_type = null
           where original_message_type is not null'''
    cursor.execute(q)


def undo_changes_to_mms():
    q = '''update message set
             type = original_message_type,
             original_message_type = null
           where original_message_type is not null'''
    cursor.execute(q)


def update_sms_to_signal():
    q = '''update message
             set type = case type
               when 20 then 10485780
               when 87 then 10485783
               when 23 then 10485783
               when 22 then 10485783
               when 24 then 10485783
               when 88 then 10485783
             end,
             read = 1,
             status = -1,
             delivery_receipt_count = 1,
             read_receipt_count = 1,
             original_message_type = type
           where type in (20,87,23,22,24,88) and m_type = 0 and original_message_type is null'''
    cursor.execute(q)


def update_signal_to_sms():
    q = '''update sms
             set type = case type
               when 10485780 then 20
               when 10485783 then 87
               when 10485784 then 87
             end,
             original_message_type = type
           where type in (10485780,10485783,10485784) and m_type = 0 and original_message_type is null'''
    cursor.execute(q)


def update_mms_to_signal():
    q = '''update mms
           set msg_box = case msg_box
             when 20 then 10485780
             when 87 then 10485783
             when 22 then 10485783
             when 23 then 10485783
             when 24 then 10485783
             when 88 then 10485783
           end,
           original_message_type = type
           where type in (20,87,22,23,24,88) and m_type in (128, 130, 132) and original_message_type is null'''
    cursor.execute(q)


def update_signal_to_mms():
    q = '''update mms
           set msg_box = case msg_box
             when 10485780 then 20
             when 10485783 then 87
             when 10485784 then 87
           end,
           original_message_type = type
           where type in (10485780,10485783,10485784) and m_type = 0 and original_message_type is null'''
    cursor.execute(q)


def add_orig_type_column():
    try:
        cursor.execute('alter table messages add column original_message_type integer default null')
    except Exception:
        pass  # ignore fail on subsequent runs


if not os.environ.get("SIG_KEY"):
    logging.info("Missing environment variable SIG_KEY, try eg: export SIG_KEY=123456789101112131415161718192")
    sys.exit(1)
if not os.environ.get("SIG_FILE"):
    logging.info("Missing environment variable SIG_FILE, try eg: export SIG_FILE=signal-2022-01-01-01-01-01.backup")
    sys.exit(1)


run_cmd("rm -rf bits signal.log")
run_cmd("mkdir -p bits")
run_cmd(f'/usr/bin/signalbackup-tools --input {os.environ["SIG_FILE"]} --output bits/ --password {os.environ["SIG_KEY"]} --no-showprogress')

# parse the sqlite database generated by github.com/bepaald/signalbackup-tools
conn = sqlite3.connect(os.path.join("bits", "database.sqlite"))
cursor = conn.cursor()


# add a column to store the original type, this let's use go back and forwards
# depending on what works best using the --undo flag. Otherwise we might change
# all to Signal messages for example, and have it not work out, and want to
# revert them back to sms again
add_orig_type_column()

print_num_sms()
print_num_signal()
print_num_mms()
print_num_signal_mms()

if args.undo:
    logging.info("Reverting previous changes")
    undo_changes_to_sms()
    undo_changes_to_mms()

elif args.tosms:
    logging.info("Converting Signal messages to SMS type")
    update_signal_to_sms()
    update_signal_to_mms()
else:
    logging.info("Converting SMS messages to Signal type")
    update_sms_to_signal()
    update_mms_to_signal()

print_num_sms()
print_num_signal()
print_num_mms()
print_num_signal_mms()

conn.commit()
cursor.close()

run_cmd("rm -rf signal-all-messages.backup")
run_cmd(f'/usr/bin/signalbackup-tools --input bits/ --output signal-all-messages.backup --opassword {os.environ["SIG_KEY"]} --no-showprogress')
run_cmd("rm -rf bits")

logging.info("Complete.")
logging.info("Created: signal-all-messages.backup")
logging.info("Now reinstall Signal and choose this file to restore")
