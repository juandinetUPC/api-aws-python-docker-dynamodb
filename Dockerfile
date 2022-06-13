FROM python:3.9.0

ENV PYTHONUNBUFFERED 1
ENV PORT=80
RUN mkdir /src
WORKDIR /src
COPY requirements.txt /src/
RUN pip install -r requirements.txt
EXPOSE $PORT
COPY ./src /src/
# RUN cd /src && python app.py
CMD python app.py
