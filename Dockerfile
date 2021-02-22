FROM python:3.7-slim

LABEL maintainer="Ed Nykaza <ed@tidepool.org>" \
      organization="Tidepool Project"

COPY requirements.txt /
RUN pip install --no-cache-dir --prefer-binary --compile -r /requirements.txt

WORKDIR /app
COPY ./ ./

EXPOSE 8050
CMD [ "python", "./src/visualization/visualize-donor-data-scatterplot.py", "./data/2019-07-17-aggregate-cgm-stats.csv" ]
