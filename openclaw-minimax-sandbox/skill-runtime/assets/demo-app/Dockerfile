FROM registry.access.redhat.com/ubi9/python-312:latest
WORKDIR /opt/app-root/src
COPY app.py index.html app.js ./
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 BIND_ADDRESS=0.0.0.0 PORT=8080
USER 1001
EXPOSE 8080
CMD ["python3", "app.py"]
