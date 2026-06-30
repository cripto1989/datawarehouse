#!/bin/bash
rm -rf function_dimensions
mkdir function_dimensions
cp lambdas/dimensions/*.py function_dimensions/
if [ -f lambdas/dimensions/requirements.txt ]; then
  pip install -r lambdas/dimensions/requirements.txt -t function_dimensions/
fi
cd function_dimensions && zip -r ../dimensions.zip . && cd ..
rm -rf function_dimensions
echo "✓ Created dimensions.zip"
