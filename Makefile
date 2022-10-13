
DOCKER := docker run -e SIG_KEY -e SIG_FILE -it -v $${PWD}:/root/ workspace

run:
	docker build -t workspace .
	# or reverse mode: --tosms
	$(DOCKER) python3 signal-message-changer.py -v

