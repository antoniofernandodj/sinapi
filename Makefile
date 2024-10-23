run:
	docker build -t sinapi -f Dockerfile .
	docker rm -f sinapi_container
	docker run -d --name sinapi_container --network host sinapi
	docker logs -f sinapi_container