#!/bin/bash
curl "https://raw.githubusercontent.com/SharifAIChallenge/final-judgment/master/resources/map.config" > map.config
java -jar /usr/local/match/match.jar $@
