FROM python:3.12-slim

RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app
COPY --chown=app:app app.py .

USER app
EXPOSE 8080

CMD ["python", "app.py"]
