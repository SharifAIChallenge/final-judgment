FROM reg.aichallenge.ir/aic/infra/final_judgment:275-e99b6780
# FROM reg.aichallenge.ir/python:3.8

# RUN apt-get update && \
# apt install -y default-jre cmake vim curl gettext && \
# pip3 install pyinstaller

WORKDIR /home

# install final_judgment
ADD ./requirements.txt ./requirements.txt
ENV PIP_NO_CACHE_DIR 1
RUN pip install -r ./requirements.txt
ADD ./ ./

# install server
RUN curl -s https://api.github.com/repos/sharifaichallenge/aic21-server/releases/latest \
| grep "browser_download_url.*jar" \
| cut -d : -f 2,3 \
| tr -d \" \
| wget -i - -O .server.jar

RUN curl "https://raw.githubusercontent.com/SharifAIChallenge/final-judgment/master/resources/map.config" > map.config

COPY server /usr/bin/server
RUN chmod +x /usr/bin/server

