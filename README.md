# Silence Detection Algorithm

## Description
Algorithm that uses the fundamental frequency to detect silences in an audio. It creates a .csv document containing every silent pauses detected in all the audios given.

## How to use ?
- From a terminal, go directly to where the detectSilences.py file is located.
- type : python detectSilences.py the_path_to_the_audios_to_analyse [the_minimum_duration_of_a_silence_to_detect_in_seconds]

## What are the arguments given ?
- the_path_to_the_audios_to_analyse :  path to where are located the audios 
- the_minimum_duration_of_a_silence_to_detect_in_seconds : it is optional. The value given in the algorithm is 0.1 seconds if a value is not given

## What it creates
It create a csv file containing all the silences detected in the audios. Each line of data represents a particular silence detected in one audio. The data are presented in the following format :

Name of File , Start of the silence in seconds, End of the silence in seconds, Duration of the silence






