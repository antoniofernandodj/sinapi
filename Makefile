load:
	git pull origin main
	docker build -t sinapi_loader -f loader.dockerfile .
	docker rm -f sinapi_loader
	docker run -d --name sinapi_loader --network host sinapi
	docker logs -f sinapi_loader

app:
	git pull origin main
	docker build -t sinapi_entrypoint -f entrypoint.dockerfile .
	docker rm -f sinapi_entrypoint
	docker run -d --name sinapi_entrypoint --network host sinapi_entrypoint
	docker logs -f sinapi_entrypoint

