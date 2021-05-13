start-dev:
	sudo docker-compose up


start-prod:
	docker-compose up --build --detach 


rebuild:
	docker-compose build

test:
	sudo docker-compose run prlmntq_etl_camara python  src/test.py