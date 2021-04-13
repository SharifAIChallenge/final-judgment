FROM reg.aichallenge.ir/aic/infra/final_judgment:275-e99b6780

# FROM reg.aichallenge.ir/python:3.8

# RUN apt-get update && \
# apt install -y default-jre cmake vim curl gettext && \
# pip3 install pyinstaller


# log directory
RUN mkdir -p /var/log/final-judgment



#################################### install final_judgment ########################### 

WORKDIR /home
ADD ./requirements.txt ./requirements.txt
ENV PIP_NO_CACHE_DIR 1
RUN pip install -r ./requirements.txt
ADD ./src ./src

#################################### install match holder #############################

# download server jar file
RUN mkdir -p /usr/local/match && \
curl -s https://api.github.com/repos/sharifaichallenge/aic21-server/releases/latest \
| grep "browser_download_url.*jar" \
| cut -d : -f 2,3 \
| tr -d '"' \
| wget -i - -O /usr/local/match/match.jar

# download server configfile
RUN curl "https://raw.githubusercontent.com/SharifAIChallenge/final-judgment/master/resources/map.config" > /usr/local/match/map.config

# install match 
COPY scripts/match.sh /usr/bin/match
RUN chmod +x /usr/bin/match

