FROM public.ecr.aws/lambda/python:3.10

RUN python -m pip install --upgrade pip setuptools wheel

# Copy requirements
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install with pre-built wheels only
RUN pip install --only-binary=:all: -r requirements.txt

# Copy all python files
COPY *.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD [ "lambda_function.lambda_handler" ]
