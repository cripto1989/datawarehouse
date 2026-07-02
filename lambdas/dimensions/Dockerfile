FROM public.ecr.aws/lambda/python:3.12

RUN python -m pip install --upgrade pip setuptools wheel

# Copy requirements
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install with pre-built wheels only
RUN pip install --only-binary=:all: -r requirements.txt

# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}
COPY db.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD [ "lambda_function.lambda_handler" ]
