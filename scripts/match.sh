#!/bin/bash
curl "https://raw.githubusercontent.com/SharifAIChallenge/final-judgment/master/resources/map.config" > /home/map.config
java -jar /usr/local/match/match.jar $@
