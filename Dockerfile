FROM python:3.7-alpine

RUN apk add --no-cache alpine-sdk taglib-dev lame flac
RUN pip install argparse pytaglib

COPY mp3-id3.py /

WORKDIR /wd
VOLUME /wd

ENTRYPOINT ["python", "/mp3-id3.py"]
CMD ["-h"]
