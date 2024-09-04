FROM python:3.9-slim AS compile-image

# Make sure we use the virtualenv:
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.9-slim AS build-image
COPY --from=compile-image /opt/venv /opt/venv

WORKDIR /app
COPY streamlit_app.py .
COPY pages pages
COPY beer_game beer_game
COPY .streamlit .streamlit

EXPOSE 5601

CMD [ "--server.address=0.0.0.0" ]
ENTRYPOINT [ "/opt/venv/bin/python3", "-m", "streamlit", "run", "streamlit_app.py" ]
