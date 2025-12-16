FROM public.ecr.aws/lambda/python:3.11

# Install system dependencies
RUN yum update -y && \
    yum install -y git && \
    yum clean all

# Copy requirements and install Python dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

# Copy source code
COPY src/ ${LAMBDA_TASK_ROOT}/

# Set the CMD to your handler (can be overridden)
CMD ["application.lambda_handlers.search_handler.lambda_handler"]