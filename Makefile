start-dev:
	sudo docker-compose up

start-prod:
	docker-compose up --build --detach 

rebuild:
	docker-compose build
