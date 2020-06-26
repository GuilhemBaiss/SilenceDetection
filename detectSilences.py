import math
import sys
import os
import parselmouth
import pandas as pd

def detect_silences(pathSound, sensibility, start, end, frame = 20):
    """
    Method that detects silences for long and short audio 
    :params pathSound: path to access to the audio 
    :params sensibility: the length of the silence pauses to detect
    :params start: parameter of where to start checking for silences in a given audio
    :params end : parameter of where to end checking for silences in a given audio
    :params frame : size of a frame that we check for silences
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
        for i in range(1, nb_of_frames):
            i+=1
            silences += __detect_silence_in_frame(pathSound, start_frame, end_frame, sensibility, high_outliers_value, low_outliers_value)
            start_frame +=frame
            end_frame +=frame

        if end_frame != end:
            #Last frame that is not equal to the frame length
            silences+= __detect_silence_in_frame(pathSound, end_frame, end, sensibility, high_outliers_value, low_outliers_value)
    else:
        silences += __detect_silence_in_frame(pathSound, start, end, sensibility, high_outliers_value, low_outliers_value)

    return silences


def __detect_silence_in_frame(pathSound, start_frame, end_frame, sensibility, high_outliers_value, low_outliers_value):
    """
    Method that detects silences in a given frame using the fundamental frequency and removes outliers using mean and standart deviation
    :params pathSound: path to access to the audio 
    :params start_frame: parameter of where to start checking for silences in a given audio
    :params end_frame : parameter of where to end checking for silences in a given audio
    :params sensibility: the length of the silence pauses to detect
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
                    if duration > sensibility:
                        silences.append({'start_time': start_frame + start_time_silence, 'end_time': start_frame + end_time_silence, 'duration': duration}) 
                        
                pauseState = False
    return silences


def get_f0_mean(pathSound, start_time, end_time):
    """
    Method that extracts the f0 mean of a particular sound found at pathMP3 location without taking in count the 0 values. 
    :params pathSound: path to the sound to analyse
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
    Function that returns the length of a sound file in seconds
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
    MINIMUM_SILENCE_DURATION = 0.1
    PATH_SOUND_FILES = sys.argv[1]

else:
    PATH_SOUND_FILES =sys.argv[1]
    MINIMUM_SILENCE_DURATION = sys.argv[2]

data = {
    'name_file' : [],
    'start_time' : [],
    'end_time' : [],
    'duration' : []
}

audio_files_list = os.listdir(PATH_SOUND_FILES)

for audios_names in audio_files_list:
    if audios_names[-3:] == "mp3" or audios_names[-3:] == "wav":
        path_sound_file = PATH_SOUND_FILES + "\\" + audios_names
        silences = detect_silences(path_sound_file, MINIMUM_SILENCE_DURATION, 0, getSoundFileLength(path_sound_file))
        for values in silences:
            data['name_file'].append(audios_names[:-4])
            data['start_time'].append(values['start_time'])
            data['end_time'].append(values['end_time'])
            data['duration'].append(values['duration'])

df = pd.DataFrame()
df = pd.DataFrame(data,columns=list(data.keys()))
df.to_csv("silences.csv", index = False)
