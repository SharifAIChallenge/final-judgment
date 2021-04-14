#!/bin/bash
curl "https://raw.githubusercontent.com/SharifAIChallenge/final-judgment/master/resources/map.config" > /usr/local/match/map.config
(cd /usr/local/match && java -jar /usr/local/match/match.jar $@)
