git-push-bit:
	git push origin main

git-push-git:
	git push github main

test-raw-events:
	pytest --rich lambdas/raw_events/
