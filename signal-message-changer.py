import os
import sys
import sqlite3
import logging
import argparse
import pkg_resources

parser = argparse.ArgumentParser(description='Update SMS messages to look like native Signal messages OR update Signal messages to look like SMS messages...')

parser.add_argument('args', nargs='*')
parser.add_argument('--tosms', '-m', dest='tosms', action='store_true', help="Cheeky mode: convert signal messages to sms (perhaps for export later...)")
parser.add_argument('--verbose', '-v', dest='verbose', action='store_true', help='Make logging more verbose')
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG if args.verbose else logging.INFO)

cur_version = pkg_resources.parse_version(str(sqlite3.sqlite_version))
min_version = pkg_resources.parse_version("3.35")

# the RETURNING syntax needs sqlite3 version >=3.35
if cur_version < min_version:
    logging.info(f"Version of sqlite3 python library is too old, upgrade to {min_version}")
    logging.info("Try the Docker version for a predictable build environment")
    sys.exit(1)


def run_cmd(cmd):
    logging.info(f"running command: {cmd}")
    r = os.popen(cmd)
    logging.info(r.read())
    if r.close() is not None:
        logging.info(f"command failed: {cmd}")
        sys.exit(r.close())


def print_num_sms():
    q = "select count(*) as tally from sms where type = 20 or type = 87 or type = 23"
    cursor.execute(q)
    (tally,) = cursor.fetchone()
    logging.info(f"Total num SMS messages: {tally}")


def print_num_signal():
    q = "select count(*) as tally from sms where type = 10485780 or type = 10485783"
    cursor.execute(q)
    (tally,) = cursor.fetchone()
    logging.info(f"Total number Signal messages: {tally}")


def change_type(fr, to):
    logging.info(f"Changing message of type {fr} to type {to}")
    q = f"update sms set type = {to}, read = 1, status = -1, delivery_receipt_count = 1, read_receipt_count = 1 where type = {fr}"
    cursor.execute(q)


if not os.environ.get("SIG_KEY"):
    logging.info("Missing environment variable SIG_KEY, try eg: export SIG_KEY=123456789101112131415161718192")
    sys.exit(1)
if not os.environ.get("SIG_FILE"):
    logging.info("Missing environment variable SIG_FILE, try eg: export SIG_FILE=signal-2022-01-01-01-01-01.backup")
    sys.exit(1)


run_cmd("rm -rf bits signal.log")
run_cmd("mkdir -p bits")
run_cmd("/usr/bin/signalbackup-tools " + os.environ["SIG_FILE"] + " " + os.environ["SIG_KEY"] + " --output bits/")

# parse the sqlite database generated by github.com/bepaald/signalbackup-tools
conn = sqlite3.connect(os.path.join("bits", "database.sqlite"))
cursor = conn.cursor()

print_num_sms()
print_num_signal()


if args.tosms:
    logging.info("Converting Signal messages to SMS type")
    change_type(10485780, 20)
    change_type(10485783, 87)
else:
    logging.info("Converting SMS messages to Signal type")
    change_type(20, 10485780)
    change_type(87, 10485783)
    change_type(23, 10485783)

print_num_sms()
print_num_signal()

conn.commit()
cursor.close()

run_cmd("rm -rf signal-all-messages.backup")
run_cmd("/usr/bin/signalbackup-tools bits/ --output signal-all-messages.backup --opassword " + os.environ["SIG_KEY"])
run_cmd("rm -rf bits")

logging.info("Complete. Created: signal-all-messages.backup now reinstall Signal and choose this file to restore.")
