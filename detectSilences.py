#@Author : Guilhem Baissus
#Algorithm written during an internship at Laboratoire d'ingénierie Cognitive Sémantique located in Montreal, Quebec
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
    sound = parselmouth.Sound(pathSound)
    sound = sound.extract_part(from_time = start , to_time = end)
    length_extracted_audio = end - start

    mean_entire_audio = get_f0_mean(pathSound, 0, getSoundFileLength(pathSound))
    standard_deviation_entire_audio = get_f0_standard_deviation(sound, 0, getSoundFileLength(pathSound))
    high_outliers_value = mean_entire_audio + 4 * standard_deviation_entire_audio
    low_outliers_value = mean_entire_audio - 2 * standard_deviation_entire_audio

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
            else:
                pass
        else:
            if values < high_outliers_value and values > low_outliers_value :
                if pauseState == True :
                    end_time_silence = pitch.xs()[index]
                    duration = end_time_silence - start_time_silence
                    if duration > minimum_silence_duration:
                        silences.append({'start_time': start_frame + start_time_silence, 'end_time': start_frame + end_time_silence, 'duration': duration}) 
                        
                pauseState = False
    return silences


def get_f0_mean(pathSound, start_time, end_time):
    """
    Method that extracts the f0 mean of a particular sound found at pathSound location without taking in account the 0 values. 
    :params pathSound: path to the sound to analyse
    :params start_time: in seconds
    :params end_time : in seconds
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

def get_f0_standard_deviation(pathSound, start_time, end_time):
    """
    Get the standard deviation around a mean
    :params pathSound: path to the sound to analyse
    :params start_time: in seconds
    :params end_time : in seconds
    :returns: standart deviation of the sound
    """
    sound = parselmouth.Sound(pathSound)
    sound = sound.extract_part(from_time = start_time , to_time = end_time)
    pitch = sound.to_pitch()
    pitch_values = pitch.selected_array['frequency']

    sum = 0
    mean = get_f0_mean(pathSound,start_time, end_time )

    for values in pitch_values:
        if values != 0:
            sum += math.pow(values - mean,2)
    
    return math.sqrt(sum / len(pitch_values))

def getSoundFileLength(pathSound):
    """
    Method that returns the length of a sound file in seconds
    :params pathSound : the path to the sound file
    :returns: the length of sound file in seconds
    """
    sound = parselmouth.Sound(pathSound)
    return sound.xmax - sound.xmin

def check_os(path, audios_names):
    """
    Method that returns the path to a precise audio file depending of the user's operating system
    params path : path to the folder containing the sound files
    params audios_name : name of the sound file that the algorithm is going to analyse
    returns : path to the specific audio file. 
    """
    if "/" in path and "\\" is not True:
        path_sound_file = PATH_SOUND_FILES + "/" + audios_names
    else:
        path_sound_file = PATH_SOUND_FILES + "\\" + audios_names
    return path_sound_file


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

        path_sound_file = check_os(PATH_SOUND_FILES, audios_names)
        silences = detect_silences(path_sound_file, MINIMUM_SILENCE_DURATION, 0, getSoundFileLength(path_sound_file))

        for values in silences:
            data['name_file'].append(audios_names[:-4])
            data['start_time'].append(values['start_time'])
            data['end_time'].append(values['end_time'])
            data['duration'].append(values['duration'])

        df = pd.DataFrame(data,columns=list(data.keys()))
        df.to_csv(audios_names+"-silences.csv", index = False)


