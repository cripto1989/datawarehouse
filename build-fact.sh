#!/bin/bash
rm -rf function_fact
mkdir function_fact
cp lambdas/fact/*.py function_fact/
if [ -f lambdas/fact/requirements.txt ]; then
  pip install -r lambdas/fact/requirements.txt -t function_fact/
fi
cd function_fact && zip -r ../fact.zip . && cd ..
rm -rf function_fact
echo "✓ Created fact.zip"
