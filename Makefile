start-dev:
	sudo docker-compose up


start-prod:
	docker-compose up --build --detach 


rebuild:
	docker-compose build

test:
	sudo docker run prlmntq_etl_camara sh -c 'python3  src/test.py'
