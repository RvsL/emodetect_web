import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.io.wavfile import write
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os
import glob
import subprocess
import time
import pandas as pd
from IPython.display import display, HTML

def extractWordFiles(filename, filedir, subdir, purge = False):

    sound_file = AudioSegment.from_wav(filename)
    audio_chunks = split_on_silence(sound_file,
        # must be silent for at least ... in ms
        min_silence_len=150,

        # consider it silent if quieter than -... dBFS
        silence_thresh=-50
    )

    if not os.path.exists(filedir + subdir):
        os.makedirs(filedir + subdir)

    # Delete tmp files in directory
    files = glob.glob(filedir + subdir + '*')
    filecount = 0
    for f in files:
        if purge:
            os.remove(f)
        else:
            filecount += 1

    for i, chunk in enumerate(audio_chunks):

        out_file = filedir + subdir + "chunk{0}.wav".format(i + filecount)
        print("exporting: ", out_file)
        chunk.export(out_file, format="wav")

def extractEMO(filename):

    openeardir = '/home/parallels/Downloads/openear/openEAR/'

    openearcommand = openeardir + 'SMILExtract -C '+ \
    openeardir + 'config/emo_IS09_emodetect.conf -I ' + \
    filename + ' -O ' + \
    openeardir + 'myresults/hobta_emobase.arff'
    #openeardir + 'myaudio/hobta.wav -O ' + \

    tmpfilename = '/home/parallels/Downloads/openear/openEAR/myresults/tmpoutput.txt'

    command = 'script -c \"' + openearcommand + '\" ' + tmpfilename

    os.chdir(openeardir)
    #print(command)
    os.system(command)
    time.sleep(5)

    with open(tmpfilename) as f:
        content = f.readlines()

    content = [x.strip() for x in content]

    res = {}
    for line in content:
        if line[:11] == "prob. class":
            rline = line.replace("prob. class \'", "")
            rline = rline.replace("\': \t", " =")
            sym = rline.find('=')
            key = rline[:sym-1]
            valstr = rline[sym+2:]
            val = float(rline[sym+2:])
            res.update({key:val})

    return res

def preparator():
    fnameCommon = 'timoshenko'

    fdir = '/home/parallels/Downloads/opensmile-2.3.0/myaudio/'
    filedir = '/home/parallels/Downloads/opensmile-2.3.0/mysplitaudio/'

    files = glob.glob(fdir + fnameCommon + '*')
    for f in files:
        fname = f.split('/')
        fname = fname[len(fname)-1]
        fname = fname.split('.')[0]

        extractWordFiles(fdir + fname + '.wav', filedir, fnameCommon + '/', True) # purge is false -> append

def processor():
    fnameCommon = 'girkin'

    # fdir = '/home/parallels/Downloads/opensmile-2.3.0/myaudio/'
    # filedir = '/home/parallels/Downloads/opensmile-2.3.0/mysplitaudio/'

    # files = glob.glob(fdir + fnameCommon + '*')
    # for f in files:
    #     fname = f.split('/')
    #     fname = fname[len(fname)-1]
    #     fname = fname.split('.')[0]

    #     extractWordFiles(fdir + fname + '.wav', filedir, fnameCommon + '/') # purge is false -> append

    rootdir = filedir + fnameCommon + '/'

    df = pd.DataFrame(columns=['anger',\
     'boredom',\
     'disgust',\
     'fear',\
     'happiness',\
     'neutral',\
     'sadness',\
     'agressiv',\
     'cheerful',\
     'intoxicated',\
     'nervous',\
     'tired',\
     'loi1',\
     'loi2',\
     'loi3'])

    files = glob.glob(rootdir + '*')
    for fname in files:
        content = extractEMO(fname)

        df1 = pd.DataFrame.from_dict(content, orient='index').T
        df = pd.concat([df, df1], ignore_index=True)

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


def prepare_report():

    # Assuming that dataframes df1 and df2 are already defined:
    # print "Dataframe 1:"
    # display(df1)
    # print "Dataframe 2:"
    # display(HTML(df2.to_html()))

    df.columns =['anger',\
     'boredom',\
     'disgust',\
     'fear',\
     'happiness',\
     'neutrality',\
     'sadness',\
     'agressivness',\
     'cheerfulness',\
     'intoxication',\
     'nervousness',\
     'tired',\
     'loi1',\
     'loi2',\
     'loi3']

    print(color.BOLD + '\nMain Table of Detected Emotions:\n' + color.END)

    df1 = df.copy()
    df1.drop(columns=['loi1', 'loi2', 'loi3'], axis=1, inplace=True)

    display(HTML(df1.to_html()))
    #print(df1)

    for col in df1:
        df1.loc[df1[col] < 1, col] = 0

    df1 = df1.loc[:, (df1.sum(axis=0) > 0)]

    print(color.BOLD + '\nCount of Main Emotions:\n' + color.END)
    print(df1.sum())

    df1.plot(title = 'Main Emotions')


    ##################################

    df1 = df.copy()
    df1.drop(columns=['loi1', 'loi2', 'loi3', 'boredom', 'neutrality', 'tired'], axis=1, inplace=True)

    for col in df1:
        df1.loc[df1[col] == 1, col] = 0
        df1.loc[df1[col] > 0, col] = 1

    df1 = df1.loc[:, (df1.sum(axis=0) > 0)]

    for col in df1:
        plt.figure()
        df1[col].plot(title = 'Hidden Emotion: ' + col)

    print(color.BOLD + '\nHidden Emotions:\n' + color.END)
    print(df1.sum())

    ###################################


    sumz = {}
    for col in df1:
        sumz.update({col:df1[col].sum()})

    df2 = pd.DataFrame.from_dict(sumz, orient='index')

    df2.columns = ['value']
    df2.plot.pie(y='value', figsize = (10,10), title = \
                'Count of Hidden Emotions')


    ####################################

    sumz = {}
    for col in df1:
        sumz.update({col:df[col].sum()})

    df2 = pd.DataFrame.from_dict(sumz, orient='index')

    df2.columns = ['value']
    df2.plot.pie(y='value', figsize = (10,10), title = \
                'Cummulative Magnitude of Hidden Emotions')

    #####################################

    df2 = df.copy()
    df2.drop(columns=['loi1', 'loi2', 'loi3'], axis=1, inplace=True)

    for col in df2:
        df2.loc[df2[col] > 0, col] = 1


    df2['lies'] = \
    ((df2['fear'] == 1 ) & ( df2['happiness'] == 1)) |\
    ((df2['fear'] == 1 ) & ( df2['cheerfulness'] == 1)) |\
    ((df2['fear'] == 1 ) & ( df2['sadness'] == 1)) |\
    ((df2['fear'] == 1 ) & ( df2['nervousness'] == 1)) |\
    ((df2['sadness'] == 1 ) & ( df2['happiness'] == 1)) |\
    ((df2['sadness'] == 1 ) & ( df2['cheerfulness'] == 1)) |\
    ((df2['sadness'] == 1 ) & ( df2['nervousness'] == 1)) |\
    ((df2['sadness'] == 1 ) & ( df2['intoxication'] == 1)) |\
    ((df2['happiness'] == 1 ) & ( df2['intoxication'] == 1)) |\
    ((df2['happiness'] == 1 ) & ( df2['nervousness'] == 1)) |\
    ((df2['cheerfulness'] == 1 ) & ( df2['intoxication'] == 1)) |\
    ((df2['cheerfulness'] == 1 ) & ( df2['nervousness'] == 1)) |\
    ((df2['intoxication'] == 1 ) & ( df2['nervousness'] == 1))

    print(color.BOLD + '\nAdditional questions needed:\n' + color.END)
    display(df2.iloc[:,0:12].loc[df2['lies'] == True])

    ####################################################


    df2.loc[df2['lies'] == 1, 'lie'] = 1
    df2.loc[df2['lies'] == 0, 'true'] = 1

    sumz = {}
    sumz.update({'lie':df2['lie'].sum()})
    sumz.update({'true':df2['true'].sum()})

    df3 = pd.DataFrame.from_dict(sumz, orient='index')

    df3.columns = ['value']
    df3.plot.pie(y='value', figsize = (10,10), title = \
                'Predicted Lies Percentage')
    print(color.BOLD + '\nComparison of Proposed Lies/Truth Qty:\n' + color.END)
    display(df3)
