FROM python:3.12-slim
WORKDIR /app

RUN sudo apt install curl

CMD ["tail", "-f", "/dev/null"]
