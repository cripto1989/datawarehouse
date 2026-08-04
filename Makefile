compile-downtime:
	@echo "\033[1;34m🚀 Compiling downtime requirements...\033[0m"
	@pip-compile lambdas/downtime/requirements.in --output-file lambdas/downtime/requirements.txt \
		&& echo "\033[1;32m✅ Downtime requirements compiled.\033[0m"

git-push-bit:
	git push origin main

git-push-git:
	git push github main

test-raw-events:
	pytest --rich lambdas/raw_events/
