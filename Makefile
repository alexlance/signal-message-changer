
DOCKER := docker run -e SIG_KEY -e SIG_FILE -it -v $${PWD}:/root/ workspace

run:
	docker build -t workspace .
	# 1. the default mode is to convert all sms/mms to Signal flavoured messages
	# 2. there is also a reverse mode: --tosms which converts ALL messages over to sms/mms type
	# 3. and an --undo flag which can take a backup file that has previously been
	#    modified by signal-message-changer and put it back to its original message types
	$(DOCKER) python3 signal-message-changer.py -v

