FROM public.ecr.aws/lambda/python:3.10

RUN python -m pip install --upgrade pip setuptools wheel

# Copy requirements
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install with pre-built wheels only
RUN pip install --only-binary=:all: -r requirements.txt

# Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD [ "app.lambda_handler" ]
