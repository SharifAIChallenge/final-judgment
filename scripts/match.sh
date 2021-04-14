#!/bin/bash
curl "https://raw.githubusercontent.com/SharifAIChallenge/final-judgment/master/resources/map.config" > /usr/local/match/map.config
java -jar /usr/local/match/match.jar $@
