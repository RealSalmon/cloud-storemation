DEFAULT_GOAL := environment
COMPOSE_SERVICE = python
COMPOSE_SHELL = ash
COMPOSE_COMMAND = docker-compose -f docker/docker-compose.yml
COMPOSE_RUN = ${COMPOSE_COMMAND} run --rm

environment:
	${COMPOSE_COMMAND} build

shell:
	${COMPOSE_RUN} ${COMPOSE_SERVICE} ${COMPOSE_SHELL}

root:
	${COMPOSE_RUN} -u root ${COMPOSE_SERVICE} ${COMPOSE_SHELL}

clean:
	${COMPOSE_COMMAND} down
	rm -rf .bash_history .ash_history .pytest_cache .coverage .python_history

.PHONY: python
python:
	${COMPOSE_RUN} ${COMPOSE_SERVICE} python

.PHONY: tests
tests:
	${COMPOSE_RUN} ${COMPOSE_SERVICE} pytest --cov-report term-missing --cov=index tests

