FROM python:3.5-onbuild
RUN apt-get install -y libjpeg62-turbo libjpeg62-turbo-dev libfreetype6 libfreetype6-dev zlib1g-dev

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update -qq && apt-get install -y locales -qq
RUN echo "pt_BR.UTF-8 UTF-8" >> /etc/locale.gen
RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
RUN locale-gen
RUN dpkg-reconfigure locales
ENV LC_ALL=pt_BR.UTF-8
ENV LANG=pt_BR.UTF-8
ENV LANGUAGE=pt_BR.UTF-8
ENV LC_CTYPE=pt_BR.UTF-8
ENV LC_COLLATE=pt_BR.UTF-8

VOLUME ["/usr/src/app/static", "/usr/src/app/media"]
EXPOSE 8000
RUN chmod +x /usr/src/app/docker-entrypoint.sh
CMD ["/usr/src/app/docker-entrypoint.sh"]