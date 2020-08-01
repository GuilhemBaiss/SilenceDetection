#@Author : Guilhem Baissus
#Algorithm written during an internship at Laboratoire d'ingénierie Cognitive Sémantique (Lincs) located in Montreal, Quebec
#My internship was supervised by Sylvie Ratté

import math
import sys
import os
import parselmouth
import pandas as pd

def detect_silences(pathSound, minimum_silence_duration, start, end, frame = 20):
    """
    Method that detects silences for long and short audios by cutting it in frame of 20 seconds 
    :params pathSound: path to access to the audio 
    :params minimum_silence_duration: the length of the silence pauses to detect
    :params start: parameter of where to start checking for silences in a given audio
    :params end : parameter of where to end checking for silences in a given audio
    :params frame : size of a frame that we check for silences (the frame size influences the accuracy of results returned by parselmouth)
    :returns: an array containing dictionnaries describing the start time, the end time and the duration of a silent pause
    """
    length_extracted_audio = end - start

    outliers = get_outliers(pathSound)
    high_outliers_value = outliers[1]
    low_outliers_value = outliers[0]

    silences = []

    if(length_extracted_audio>frame):
        nb_of_frames = int(length_extracted_audio/frame)
        start_frame = start
        end_frame = start_frame + frame
        for i in range(1, nb_of_frames+1):
            silences += __detect_silence_in_frame(pathSound, start_frame, end_frame, minimum_silence_duration, high_outliers_value,low_outliers_value )
            start_frame +=frame
            end_frame +=frame

        last_end_frame = end_frame - frame
        if last_end_frame < end and end - last_end_frame > 1:
            #Last frame that is not equal to the frame length
            silences+= __detect_silence_in_frame(pathSound, last_end_frame, end, minimum_silence_duration, high_outliers_value, low_outliers_value)
    else:
        silences += __detect_silence_in_frame(pathSound, start, end, minimum_silence_duration, high_outliers_value, low_outliers_value)

    return silences


def __detect_silence_in_frame(pathSound, start_frame, end_frame, minimum_silence_duration, high_outliers_value, low_outliers_value):
    """
    Method that detects silences in a given frame using the fundamental frequency and removes outliers
    :params pathSound: path to access to the audio 
    :params start_frame: parameter of where to start checking for silences in a given audio
    :params end_frame : parameter of where to end checking for silences in a given audio
    :params minimum_silence_duration: the length of the silence pauses to detect
    :params high_outliers_value: values higher than this parameter are considered as outliers
    :params low_outliers_value: values lower than this parameter are considered as outliers
    :returns: an array containing dictionnaries describing the start time, the end time and the duration of a silent pause
    """

    silences = []

    sound = parselmouth.Sound(pathSound)
    sound = sound.extract_part(from_time = start_frame , to_time = end_frame)
    pitch = sound.to_pitch()
    pitch_values = pitch.selected_array['frequency']

    start_time_silence = -1
    end_time_silence = -1
    duration = -1
    pauseState = False
    
    for index, values in enumerate(pitch_values):
        if values==0:
            if pauseState == False:
                start_time_silence = pitch.xs()[index]
                pauseState = True
            #Check if there is silence at the end of the audio
            elif pauseState == True and pitch.xs()[index] == pitch.xs()[-1] and (values > high_outliers_value or values < low_outliers_value):
                silences.append({'start_time': start_frame + start_time_silence, 'end_time': start_frame + pitch.xs()[index], 'duration': pitch.xs()[index] - start_time_silence})
        else:
            if values < high_outliers_value and values > low_outliers_value :
                if pauseState == True :
                    end_time_silence = pitch.xs()[index]
                    duration = end_time_silence - start_time_silence
                    if duration > minimum_silence_duration:
                        silences.append({'start_time': start_frame + start_time_silence, 'end_time': start_frame + end_time_silence, 'duration': duration}) 
                        
                pauseState = False
    return silences


def get_f0_mean(pathSound, start_time, end_time, voice_max_frequency, voice_min_frequency):
    """
    Method that extracts the f0 mean of a particular sound found at pathSound location without taking in account the 0 values. 
    :params pathSound: path to the sound to analyse
    :params start_time: in seconds
    :params end_time : in seconds
    :params voice_max_frequency : maximum frequency of a human being (adult man or adult female)
    :params voice_min_frequency : minimum frequency of a human being (adult man or adult female)
    :returns: mean f0 in the given time
    """
    sound = parselmouth.Sound(pathSound)
    sound = sound.extract_part(from_time = start_time , to_time = end_time)
    pitch = sound.to_pitch()
    pitch_values = pitch.selected_array['frequency']
    pitch_mean = 0
    size= 1
    for values in pitch_values:
        if values!=0:
            pitch_mean += values
            size +=1

    return pitch_mean/size

def get_f0_standard_deviation(pathSound, start_time, end_time, voice_max_frequency, voice_min_frequency):
    """
    Get the standard deviation around a mean
    :params pathSound: path to the sound to analyse
    :params start_time: in seconds
    :params end_time : in seconds
    :params voice_max_frequency : maximum frequency of a human being (adult man or adult female)
    :params voice_min_frequency : minimum frequency of a human being (adult man or adult female)
    :returns: standart deviation of the sound
    """
    sound = parselmouth.Sound(pathSound)
    sound = sound.extract_part(from_time = start_time , to_time = end_time)
    pitch = sound.to_pitch()
    pitch_values = pitch.selected_array['frequency']

    sum = 0
    mean = get_f0_mean(pathSound,start_time, end_time, voice_max_frequency, voice_min_frequency)

    for values in pitch_values:
        if values != 0:
            sum += math.pow(values - mean,2)
    
    return math.sqrt(sum / len(pitch_values))

def get_outliers(pathSound, voice_max_frequency = 300, voice_min_frequency = 50):
    """
    Method that returns the borders to where to analyse the voice signal
    :params pathSound : path to the audio file
    :params voice_max_frequency : maximum frequency of a human being (adult man or adult female)
    :params voice_min_frequency : minimum frequency of a human being (adult man or adult female)
    """
    outliers = []

    length_audio = getSoundFileLength(pathSound)
    mean_entire_audio = get_f0_mean(pathSound, 0, length_audio, voice_max_frequency, voice_min_frequency)
    standard_deviation_entire_audio = get_f0_standard_deviation(pathSound, 0, length_audio, voice_max_frequency, voice_min_frequency)
    
    high_outliers_value = mean_entire_audio + 4*standard_deviation_entire_audio
    if high_outliers_value > voice_max_frequency:
        high_outliers_value = voice_max_frequency

    low_outliers_value = mean_entire_audio - 2*standard_deviation_entire_audio
    if low_outliers_value < voice_min_frequency:
        low_outliers_value = voice_min_frequency

    outliers.append(low_outliers_value)
    outliers.append(high_outliers_value)

    return outliers
    
def getSoundFileLength(pathSound):
    """
    Method that returns the length of a sound file in seconds
    :params pathSound : the path to the sound file
    :returns: the length of sound file in seconds
    """
    sound = parselmouth.Sound(pathSound)
    return sound.xmax - sound.xmin

#-----------------------------------------------------------------------------------------------------------

if len(sys.argv) ==1:
    print("ERROR : python pythonFile.py path_to_sound_files [minimum_silence_duration]")
    sys.exit()

elif len(sys.argv) > 3:
    print("Error : too many arguments given")
    sys.exit()
    
elif len(sys.argv) == 2:
    MINIMUM_SILENCE_DURATION = 0.5
    PATH_SOUND_FILES = sys.argv[1]

else:
    PATH_SOUND_FILES =sys.argv[1]
    MINIMUM_SILENCE_DURATION = sys.argv[2]


df = pd.DataFrame()

audio_files_list = os.listdir(PATH_SOUND_FILES)

for audios_names in audio_files_list:
    if audios_names[-3:] == "mp3" or audios_names[-3:] == "wav":
        print("Extracting silences for : {}".format(audios_names))

        data = {
            'name_file' : [],
            'start_time' : [],
            'end_time' : [],
            'duration' : []
        }

        path_sound_file = os.path.join(path_sound_file,audios_names)
        silences = detect_silences(path_sound_file, MINIMUM_SILENCE_DURATION, 0, getSoundFileLength(path_sound_file))

        for values in silences:
            data['name_file'].append(audios_names[:-4])
            data['start_time'].append(values['start_time'])
            data['end_time'].append(values['end_time'])
            data['duration'].append(values['duration'])

        df = pd.DataFrame(data,columns=list(data.keys()))
        df.to_csv(audios_names+"-silences.csv", index = False)


