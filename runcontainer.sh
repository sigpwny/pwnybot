# Stolen from Ravi
docker run --rm -it \
	--volume="`pwd`:/source:rw" \
	-e LANG=C.UTF-8 \
	--security-opt seccomp=unconfined \
	pycontainer