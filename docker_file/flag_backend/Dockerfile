FROM python:3.6
WORKDIR /opt/tq

COPY ./requirements.txt ./
RUN mkdir $HOME/.pip && echo "[global]\nindex-url=https://mirrors.aliyun.com/pypi/simple/" > $HOME/.pip/pip.conf \
&& pip install --no-cache-dir -r requirements.txt \
&& CFLAGS="-I/usr/local/opt/openssl/include" LDFLAGS="-L/usr/local/opt/openssl/lib" UWSGI_PROFILE_OVERRIDE=ssl=true pip install uwsgi -I --no-cache-dir \

