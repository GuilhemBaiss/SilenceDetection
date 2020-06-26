# Silent Detection in a Dialogue Algorithm

## Description
Algorithm that detects silences in a dialogue from a given audio. It creates a .csv document containing every silent pauses detected.

## How to use ?
- From a terminal, go directly to where the detectSilences.py file is located.
- type : python detectSilences.py the_path_to_the_audios_to_analyse [the_minimum_duration_of_a_silence_to_detect_in_seconds]

## What are the arguments given ?
- the_path_to_the_audios_to_analyse :  path to where are located the audios 
- the_minimum_duration_of_a_silence_to_detect_in_seconds : it is optional. If the value is not given as an argument, 0.1 seconds will be used in the algorithm.

## What it creates
It create a csv file containing all the silences detected in the audios. Each line of data represents a particular silence detected in one audio. The data are presented in the following format :

Name of File , Start of the silence in seconds, End of the silence in seconds, Duration of the silence

## How does this algorithm work?
The algorithm uses the parselmouth library to access to the fundamental frequencies of the audio. In fact, a fundamental frequency of zero will represent a silent. The algorithm removes outliers that could be created by ambiant sounds.






