import numpy as np
import os
import glob
import warnings
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

groundTruthAll = [
  {'prefix': 'original_video1', 'frames': 313, 'segments': ((36,70), (160,250))},
  {'prefix': 'original_video2', 'frames': 1145, 'segments': ((933,1030),)},
  {'prefix': 'original_video3', 'frames': 649, 'segments': ()},
  {'prefix': 'original_video4', 'frames': 949, 'segments': ((740,881),)},
  {'prefix': 'uni_ulm_Sequence2_1', 'frames': 947, 'segments': ((500,925),)},
  {'prefix': 'uni_ulm_Sequence2_4', 'frames': 947, 'segments': ((500,925),)},
  {'prefix': 'citinews1.', 'frames': 389, 'segments': ((1,386),)},
  {'prefix': 'citinews1_stabilized', 'frames': 389, 'segments': ((1,389),)},
  {'prefix': 'citinews2.', 'frames': 245, 'segments': ((1,245),)},
  {'prefix': 'citinews2_stabilized', 'frames': 245, 'segments': ((1,245),)},
  {'prefix': 'citinews3.', 'frames': 279, 'segments': ((1,279),)},
  {'prefix': 'citinews3_stabilized', 'frames': 279, 'segments': ((1,279),)},
  {'prefix': 'gram_rtm_uah_Urban1', 'frames': 23435, 'segments': ()},#((1500,1880), (2410,2960), (3680,3810), (4470,4970), (5670,6040), (9490,9515), (9720,10190), (11060,11230), (13010,13300), (13615,13670), (13820,14340), (16610,16740), (17090,17450), (19345,19470), (19970,20590), (20770,20880), (21260,21610))},
  {'prefix': 'uni_ulm_Sequence1a_1', 'frames': 2419, 'segments': ()},
  {'prefix': 'uni_ulm_Sequence1a_4', 'frames': 2419, 'segments': ()},
  {'prefix': 'uni_ulm_Sequence3_1', 'frames': 1020, 'segments': ()},
  {'prefix': 'uni_ulm_Sequence3_4', 'frames': 1020, 'segments': ()},
  {'prefix': 'changedetection_highway', 'frames': 1700, 'segments': ()},
  {'prefix': 'changedetection_streetLight', 'frames': 3200, 'segments': ()},
  {'prefix': 'changedetection_traffic', 'frames': 1570, 'segments': ()},
  {'prefix': 'gram_rtm_uah_M30.', 'frames': 7520, 'segments': ()},
  {'prefix': 'gram_rtm_uah_M30HD', 'frames': 9390, 'segments': ()},
  {'prefix': 'jodoin_urbantracker_rene', 'frames': 8501, 'segments': ()},
  {'prefix': 'jodoin_urbantracker_rouen', 'frames': 628, 'segments': ()},
  {'prefix': 'jodoin_urbantracker_sherbrooke', 'frames': 4000, 'segments': ()},
  {'prefix': 'jodoin_urbantracker_stmarc', 'frames': 2000, 'segments': ()},
]

groundTruth = [d for d in groundTruthAll if d['prefix'] in (
  'original_video1', 'original_video2', 'original_video4', #'citinews3_stabilized',
  'uni_ulm_Sequence1a_1', 'uni_ulm_Sequence1a_4',
  'uni_ulm_Sequence2_1',  'uni_ulm_Sequence2_4',
  'uni_ulm_Sequence3_1',  'uni_ulm_Sequence3_4',
  'changedetection_highway', 'changedetection_streetLight', 'changedetection_traffic',
  )]


mustHaveTP = (
  'original_video1', 'original_video2', 'original_video4', #'citinews3_stabilized',
  'uni_ulm_Sequence2_1', 'uni_ulm_Sequence2_4',
)

def drawGroundTruth(axs, yspan, frames, segments):
  #print(f'MIRA 1: {yspan} / {frames}')
  axs.add_patch(Rectangle((1,yspan[0]), frames, 1, facecolor='#00FF00'))
  for segment in segments:
    #print(f'MIRA 2: {yspan} / {segment}')
    axs.add_patch(Rectangle((segment[0],yspan[0]), segment[1]-segment[0], 1, facecolor='#FF0000'))

def drawAllGT():
  fig, axs = plt.subplots(1, 1)
  maxx=0
  y = 1
  for gt in groundTruth:
    if True:#gt['prefix'] in ('original_video1', 'original_video2', 'original_video4', 'uni_ulm_Sequence2_1'):
      drawGroundTruth(axs, (y, y+1), gt['frames'], gt['segments'])
      y=y+2
      maxx = max(maxx, gt['frames'])
  #print(f'MIRA 2: {maxx}')
  axs.set_xlim([0, maxx+1])
  axs.set_ylim([0.9, y-0.1])
  axs.set_xlabel('frame number')
  #axs.set_yticks((1.5, 3.5, 5.5, 7.5))
  axs.set_yticks(np.arange(1.5, 12*2, 2))
  #axs.set_yticklabels(('Video 1', 'Video 2', 'Video 4', 'seq. 2 - SK_4'))
  axs.set_yticklabels(('Video 1', 'Video 2', 'Video 4', 'seq. 1a - SK_1', 'seq. 1a - SK_4', 'seq. 2 - SK_1', 'seq. 2 - SK_4', 'seq. 3 - SK_1', 'seq. 3 - SK_4', 'highway', 'streetLight', 'traffic'))
  fig.set_tight_layout(True)
  plt.savefig('groundtruth2.pdf', format='pdf')
  #plt.show()

drawAllGT()
sys.exit(0)


def inAnySegment(values, segments):
  result = np.zeros(values.shape, dtype=np.bool_)
  for segment in segments:
    result = np.logical_or(result, np.logical_and(values>=segment[0], values<=segment[1]))
  return result

def computeSummaries(directory, groundTruth=groundTruth):
  shape  = (len(groundTruth),)
  TPs    = np.zeros(shape, dtype=np.float64)
  FPs    = np.zeros(shape, dtype=np.float64)
  FNs    = np.zeros(shape, dtype=np.float64)
  TNs    = np.zeros(shape, dtype=np.float64)
  GT_Ps  = np.zeros(shape, dtype=np.float64)
  frames = np.zeros(shape, dtype=np.float64)
  precs  = np.zeros(shape, dtype=np.float64)
  recs   = np.zeros(shape, dtype=np.float64)
  spaccs = np.zeros(shape, dtype=np.float64)
  names  = []
  for i,g in enumerate(groundTruth):
    TP = 0
    FP = 0
    FN = 0
    TN = 0
    prefix     = g['prefix']
    nframes    = g['frames']
    segments   = g['segments']
    pattern    = os.path.join(directory, prefix)+'*.txt'
    files      = glob.glob(pattern)
    if len(files)!=1:
      raise Exception(f'There should be just one file for {pattern}. Files: {files}')
    with warnings.catch_warnings():
      warnings.filterwarnings('ignore', 'loadtxt: Empty input file')
      anomFrames = np.loadtxt(files[0], comments=':', dtype=np.int32)
    #print(f'MIRA: {anomFrames.shape} for {files[0]}')
    if anomFrames.shape==():
      #import code; code.interact(local=locals())
      anomFrames = anomFrames.reshape((-1,))
    #repeated   = np.diff(anomFrames, prepend=1)
    #anomFrames = anomFrames[repeated!=0]
    allFrames  = np.arange(1, nframes+1, dtype=np.int32)
    GT_P       = inAnySegment(allFrames, segments)
    GT_N       = np.logical_not(GT_P)
    detected   = np.bincount(anomFrames, minlength=nframes+1)[1:]
    not_detected = detected==0
    TP = np.logical_and(GT_P, detected==1)
    FP = np.logical_or(np.logical_and(GT_N, detected), np.logical_and(GT_P, detected>1))
    FN = np.logical_and(GT_P, not_detected)
    TN = np.logical_and(GT_N, not_detected)
    #detected   = np.zeros(allFrames.shape, dtype=np.bool_)
    #detected[anomFrames] = True
    #not_detected         = np.logical_not(detected)
    #TP = np.logical_and(GT_P, detected)
    #FP = np.logical_and(GT_N, detected)
    #FN = np.logical_and(GT_P, not_detected)
    #TN = np.logical_and(GT_N, not_detected)
    TPs[i]    = TP.sum()
    FPs[i]    = FP.sum()
    FNs[i]    = FN.sum()
    TNs[i]    = TN.sum()
    GT_Ps[i]  = GT_P.sum()
    if TPs[i]==0:
      if FPs[i]==0 and FNs[i]==0:
        precs[i]  = 1
        recs[i]   = 1
        spaccs[i] = 1
      else:
        precs[i]  = 0
        recs[i]   = 0
        spaccs[i] = 0
    else:
      precs[i]  = TPs[i]/(TPs[i]+FPs[i])
      recs[i]   = TPs[i]/(TPs[i]+FNs[i])
      spaccs[i] = TPs[i]/(TPs[i]+FNs[i]+FPs[i])
    frames[i] = nframes
    names.append(prefix)
  allCriticalTPsArePresent = all(tp>0 for tp,name in zip(TPs,names) if name in mustHaveTP)
  return {'TP': TPs, 'FP': FPs, 'TN': TNs, 'FN': FNs, 'GT_P': GT_Ps, 'frames': frames, 'precision': precs, 'recall': recs, 'spacc': spaccs, 'name': names, 'allCriticalTPsArePresent': allCriticalTPsArePresent}

def writeSummarySingleExperiment(path, summary):
  name,frames,TP,FP,TN,FN,GT_P,precision,recall,spacc,allCriticalTPsArePresent = summary['name'], summary['frames'], summary['TP'], summary['FP'], summary['TN'], summary['FN'], summary['GT_P'], summary['precision'], summary['recall'], summary['spacc'], summary['allCriticalTPsArePresent']
  #import code; code.interact(local=locals())
  with open(path, 'w') as f:
    f.write('name,frames,GT_P,TP,FP,TN,FN,precision,recall,spatial accuracy\n')
    for i in range(len(summary['TP'])):
      f.write(f'{name[i]},{frames[i]},{GT_P[i]},{TP[i]},{FP[i]},{TN[i]},{FN[i]},{precision[i]},{recall[i]},{spacc[i]}\n')
    f.write(f',,,,,,,{np.mean(precision)},{np.mean(recall)},{np.mean(spacc)},{allCriticalTPsArePresent}\n')
    f.write(f',,,,,,,avg. precision,avg. recall,avg. spatial accuracy,allCriticalTPsArePresent\n')

def writeSummariesSingleExperiment(path, summaries):
  with open(path, 'w') as f:
    for directory, spec, summary in summaries:
      name,frames,TP,FP,TN,FN,GT_P,precision,recall,spacc,allCriticalTPsArePresent = summary['name'], summary['frames'], summary['TP'], summary['FP'], summary['TN'], summary['FN'], summary['GT_P'], summary['precision'], summary['recall'], summary['spacc'], summary['allCriticalTPsArePresent']
      f.write(f'{directory}\n')
      f.write('name,frames,GT_P,TP,FP,TN,FN,precision,recall,spatial accuracy,allCriticalTPsArePresent\n')
      for i in range(len(summary['TP'])):
        f.write(f'{name[i]},{frames[i]},{GT_P[i]},{TP[i]},{FP[i]},{TN[i]},{FN[i]},{precision[i]},{recall[i]},{spacc[i]},{allCriticalTPsArePresent}\n')
      f.write(f',,,,,,,{np.mean(precision)},{np.mean(recall)},{np.mean(spacc)},{allCriticalTPsArePresent}\n')
      f.write(f',,,,,,,avg. precision,avg.recall,avg. spatial accuracy,allCriticalTPsArePresent\n\n')

def writeTable(path, summaries, fieldname):
  ds = (0,1)
  ss = (3,4,5,6)
  ps = (0.99,0.98,0.95,0.9,0.85)
  Ps = ','.join(f'P={p}' for p in ps)
  with open(path, 'w') as f:
    names = summaries[0][2]['name']
    for i,name in enumerate(names):
      for d in ds:
        f.write(f'{name},{Ps},DLS=={d}\n')
        for s in ss:
          values=[]
          for p in ps:
            _,_,match = getSingleMatch(summaries, {'S': s, 'P': p, 'DLS': d})
            values.append(match[fieldname][i])
          valuesstr = ','.join(f'{v}' for v in values)
          f.write(f'S={s},{valuesstr}\n')
        f.write('\n')

def getMatches(summaries, spec):
  matches = []
  for tup in summaries:
    thisspec = tup[1]
    if all(thisspec[name]==value for name, value in spec.items()):
      matches.append(tup)
  return matches

def getSingleMatch(summaries, spec):
  matches = getMatches(summaries, spec)
  if len(matches)!=1:
    #import code; code.interact(local=locals())
    raise Exception(f'There should be only one match for this spec: {spec}, but there are {len(matches)}')
  return matches[0]

def writeSummaryAllExperiments(path, summaries, specs, header, rowTemplate):
  null = ''
  with open(path, 'w') as f:
    f.write(header)
    f.write('\n')
    for spec in specs:
      _, _, match = getSingleMatch(summaries, spec)
      strf = f'f"{rowTemplate}"'
      f.write(eval(strf))
      f.write('\n')

def getCurves(summaries, specsToShow, specName, measureNames, funs):
  xs  = []
  yss = [[] for _ in range(len(measureNames))]
  for s in specsToShow:
    _, spec, match = getSingleMatch(summaries, s)
    xs.append(spec[specName])
    for i,(mn,fun) in enumerate(zip(measureNames, funs)):
      yss[i].append(fun(match[mn]))
      #print(f'Adding for {specName} value {xs[-1]}, for {mn} value {yss[i][-1]}')
  return xs, yss

def showGraph(summaries, specsToShow, specName, measureNames, funs):
  xs, yss = getCurves(summaries, specsToShow, specName, measureNames, funs)
  everything = []
  for ys in yss:
    everything.append(xs)
    everything.append(ys)
  fig, axs = plt.subplots(1, 2)
  axs[0].plot(*everything)
  axs[0].legend(measureNames)
  axs[1].plot(yss[1], yss[0])
  axs[1].set_xlabel(measureNames[1])
  axs[1].set_ylabel(measureNames[0])
  plt.show()

def writeAllSummaries(prefixpath, directories, specs, header, rowTemplate):
  summaries = []
  for d, spec in directories:
    s = computeSummaries(os.path.join(prefixpath, d))
    summaries.append((d,spec,s))
    #writeSummarySingleExperiment(os.path.join(d, 'results.csv'), s)
  writeSummariesSingleExperiment(os.path.join(prefixpath, 'allresults.csv'), summaries)
  writeSummaryAllExperiments(os.path.join(prefixpath, 'summary.csv'), summaries, specs, header, rowTemplate)
  return summaries

def getBaseData():
  directories = [
    ('quantiles_vector_mean_N005_P60_S3_Percentile0.85_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_True', {'S': 3, 'P': 0.85, 'BC': 0, 'DLS': 1, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S3_Percentile0.9_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_True', {'S': 3, 'P': 0.9, 'BC': 0, 'DLS': 1, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S3_Percentile0.95_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_True', {'S': 3, 'P': 0.95, 'BC': 0, 'DLS': 1, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S3_Percentile0.98_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_True', {'S': 3, 'P': 0.98, 'BC': 0, 'DLS': 1, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S3_Percentile0.99_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_True', {'S': 3, 'P': 0.99, 'BC': 0, 'DLS': 1, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S4_Percentile0.85_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_True', {'S': 4, 'P': 0.85, 'BC': 0, 'DLS': 1, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S4_Percentile0.9_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_True', {'S': 4, 'P': 0.9, 'BC': 0, 'DLS': 1, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S4_Percentile0.95_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_True', {'S': 4, 'P': 0.95, 'BC': 0, 'DLS': 1, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S4_Percentile0.98_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_True', {'S': 4, 'P': 0.98, 'BC': 0, 'DLS': 1, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S4_Percentile0.99_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_True', {'S': 4, 'P': 0.99, 'BC': 0, 'DLS': 1, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S5_Percentile0.85_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_True', {'S': 5, 'P': 0.85, 'BC': 0, 'DLS': 1, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S5_Percentile0.9_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_True', {'S': 5, 'P': 0.9, 'BC': 0, 'DLS': 1, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S5_Percentile0.95_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_True', {'S': 5, 'P': 0.95, 'BC': 0, 'DLS': 1, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S5_Percentile0.98_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_True', {'S': 5, 'P': 0.98, 'BC': 0, 'DLS': 1, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S5_Percentile0.99_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_True', {'S': 5, 'P': 0.99, 'BC': 0, 'DLS': 1, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S6_Percentile0.85_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_True', {'S': 6, 'P': 0.85, 'BC': 0, 'DLS': 1, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S6_Percentile0.9_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_True', {'S': 6, 'P': 0.9, 'BC': 0, 'DLS': 1, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S6_Percentile0.95_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_True', {'S': 6, 'P': 0.95, 'BC': 0, 'DLS': 1, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S6_Percentile0.98_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_True', {'S': 6, 'P': 0.98, 'BC': 0, 'DLS': 1, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S6_Percentile0.99_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_True', {'S': 6, 'P': 0.99, 'BC': 0, 'DLS': 1, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S3_Percentile0.85_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_False', {'S': 3, 'P': 0.85, 'BC': 0, 'DLS': 0, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S3_Percentile0.9_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_False', {'S': 3, 'P': 0.9, 'BC': 0, 'DLS': 0, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S3_Percentile0.95_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_False', {'S': 3, 'P': 0.95, 'BC': 0, 'DLS': 0, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S3_Percentile0.98_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_False', {'S': 3, 'P': 0.98, 'BC': 0, 'DLS': 0, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S3_Percentile0.99_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_False', {'S': 3, 'P': 0.99, 'BC': 0, 'DLS': 0, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S4_Percentile0.85_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_False', {'S': 4, 'P': 0.85, 'BC': 0, 'DLS': 0, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S4_Percentile0.9_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_False', {'S': 4, 'P': 0.9, 'BC': 0, 'DLS': 0, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S4_Percentile0.95_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_False', {'S': 4, 'P': 0.95, 'BC': 0, 'DLS': 0, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S4_Percentile0.98_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_False', {'S': 4, 'P': 0.98, 'BC': 0, 'DLS': 0, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S4_Percentile0.99_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_False', {'S': 4, 'P': 0.99, 'BC': 0, 'DLS': 0, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S5_Percentile0.85_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_False', {'S': 5, 'P': 0.85, 'BC': 0, 'DLS': 0, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S5_Percentile0.9_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_False', {'S': 5, 'P': 0.9, 'BC': 0, 'DLS': 0, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S5_Percentile0.95_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_False', {'S': 5, 'P': 0.95, 'BC': 0, 'DLS': 0, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S5_Percentile0.98_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_False', {'S': 5, 'P': 0.98, 'BC': 0, 'DLS': 0, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S5_Percentile0.99_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_False', {'S': 5, 'P': 0.99, 'BC': 0, 'DLS': 0, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S6_Percentile0.85_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_False', {'S': 6, 'P': 0.85, 'BC': 0, 'DLS': 0, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S6_Percentile0.9_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_False', {'S': 6, 'P': 0.9, 'BC': 0, 'DLS': 0, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S6_Percentile0.95_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_False', {'S': 6, 'P': 0.95, 'BC': 0, 'DLS': 0, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S6_Percentile0.98_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_False', {'S': 6, 'P': 0.98, 'BC': 0, 'DLS': 0, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    ('quantiles_vector_mean_N005_P60_S6_Percentile0.99_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_False', {'S': 6, 'P': 0.99, 'BC': 0, 'DLS': 0, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
  ]
  prefixpath = '/media/Data/experiments/cuadricula_S_Percent/'
  specs = [{'S': s, 'P': p, 'DLS': d} for s in (3,4,5,6) for p in (0.85,0.9,0.95,0.98,0.99) for d in (0,1)]
  header = 'anomaly_scale,percentile_threshold,DLS,average precision,average recall,average spatial accuracy,allCriticalTPsArePresent,nonzero precision,nonzero recall,nonzero spatial accuracy,total FP,total FN'
  rowTemplate = "{spec.get('S',null)},{spec.get('P',null)},{spec.get('DLS',null)},{match['precision'].mean()},{match['recall'].mean()},{match['spacc'].mean()},{match['allCriticalTPsArePresent']},{(match['precision']!=0).sum()},{(match['recall']!=0).sum()},{(match['spacc']!=0).sum()},{match['FP'].sum()},{match['FN'].sum()}"
  return {'prefixpath': prefixpath, 'directories': directories, 'specs': specs, 'header': header, 'rowTemplate': rowTemplate}

def getDataByBackbone(backbone, pref):
  directories = [
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_no_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.1_allvehicles_use_distance_limit_small_False', {'BC': 0, 'DLS': 0, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.1, 'JSV': 0}),
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_no_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.2_allvehicles_use_distance_limit_small_False', {'BC': 0, 'DLS': 0, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.2, 'JSV': 0}),
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_no_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.3_allvehicles_use_distance_limit_small_False', {'BC': 0, 'DLS': 0, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.3, 'JSV': 0}),
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_no_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.4_allvehicles_use_distance_limit_small_False', {'BC': 0, 'DLS': 0, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.4, 'JSV': 0}),
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_no_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.5_allvehicles_use_distance_limit_small_False', {'BC': 0, 'DLS': 0, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.5, 'JSV': 0}),

    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_no_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.1_allvehicles_use_distance_limit_small_True', {'BC': 0, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.1, 'JSV': 0}),
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_no_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.2_allvehicles_use_distance_limit_small_True', {'BC': 0, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.2, 'JSV': 0}),
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_no_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.3_allvehicles_use_distance_limit_small_True', {'BC': 0, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.3, 'JSV': 0}),
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_no_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.4_allvehicles_use_distance_limit_small_True', {'BC': 0, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.4, 'JSV': 0}),
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_no_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.5_allvehicles_use_distance_limit_small_True', {'BC': 0, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.5, 'JSV': 0}),

    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_no_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.1_smallvehicles_use_distance_limit_small_True', {'BC': 0, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.1, 'JSV': 1}),
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_no_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.2_smallvehicles_use_distance_limit_small_True', {'BC': 0, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.2, 'JSV': 1}),
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_no_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.3_smallvehicles_use_distance_limit_small_True', {'BC': 0, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.3, 'JSV': 1}),
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_no_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.4_smallvehicles_use_distance_limit_small_True', {'BC': 0, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.4, 'JSV': 1}),
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_no_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.5_smallvehicles_use_distance_limit_small_True', {'BC': 0, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.5, 'JSV': 1}),

    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.1_allvehicles_use_distance_limit_small_False', {'BC': 1, 'DLS': 0, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.1, 'JSV': 0}),
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.2_allvehicles_use_distance_limit_small_False', {'BC': 1, 'DLS': 0, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.2, 'JSV': 0}),
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.3_allvehicles_use_distance_limit_small_False', {'BC': 1, 'DLS': 0, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.3, 'JSV': 0}),
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.4_allvehicles_use_distance_limit_small_False', {'BC': 1, 'DLS': 0, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.4, 'JSV': 0}),
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.5_allvehicles_use_distance_limit_small_False', {'BC': 1, 'DLS': 0, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.5, 'JSV': 0}),

    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.1_allvehicles_use_distance_limit_small_True', {'BC': 1, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.1, 'JSV': 0}),
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.2_allvehicles_use_distance_limit_small_True', {'BC': 1, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.2, 'JSV': 0}),
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.3_allvehicles_use_distance_limit_small_True', {'BC': 1, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.3, 'JSV': 0}),
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.4_allvehicles_use_distance_limit_small_True', {'BC': 1, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.4, 'JSV': 0}),
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.5_allvehicles_use_distance_limit_small_True', {'BC': 1, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.5, 'JSV': 0}),

    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.1_smallvehicles_use_distance_limit_small_True', {'BC': 1, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.1, 'JSV': 1}),
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.2_smallvehicles_use_distance_limit_small_True', {'BC': 1, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.2, 'JSV': 1}),
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.3_smallvehicles_use_distance_limit_small_True', {'BC': 1, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.3, 'JSV': 1}),
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.4_smallvehicles_use_distance_limit_small_True', {'BC': 1, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.4, 'JSV': 1}),
    (f'{pref}quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_classic_THR0.25_mindim0_{backbone}_thresh_0.5_smallvehicles_use_distance_limit_small_True', {'BC': 1, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'BBT': 0.5, 'JSV': 1}),
  ]
  thrs = (0.1,0.2,0.3,0.4,0.5)
  specs = (
    [{'BC': 0, 'DLS': 0, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'JSV': 0, 'BBT': x} for x in thrs]+
    [{'BC': 0, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'JSV': 0, 'BBT': x} for x in thrs]+
    [{'BC': 0, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'JSV': 1, 'BBT': x} for x in thrs]+
    [{'BC': 1, 'DLS': 0, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'JSV': 0, 'BBT': x} for x in thrs]+
    [{'BC': 1, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'JSV': 0, 'BBT': x} for x in thrs]+
    [{'BC': 1, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': backbone, 'JSV': 1, 'BBT': x} for x in thrs]+
    [])
  return directories, specs

def getOurData():
  prefixpath = '/media/Data/experiments/to_measure/'
  prefixOurData = '/media/Data/experiments/to_measure_nofeatures/'
  dirs_resnet18, specs_resnet18 = getDataByBackbone('resnet18', '/media/Data/experiments/to_measure_resnet18/')
  dirs_resnet101, specs_resnet101 = getDataByBackbone('resnet101', '/media/Data/experiments/to_measure_resnet101/')
  dirs_vgg11_bn, specs_vgg11_bn = getDataByBackbone('vgg11_bn', '/media/Data/experiments/to_measure_vgg11/')
  dirs_vgg19_bn, specs_vgg19_bn = getDataByBackbone('vgg19_bn', '/media/Data/experiments/to_measure_vgg19/')
  directories = [
  #BC==BORDER CORRECTION
  #DLS==USE DISTANCE LIMIT SMALL
  #FT==USE FEATURES
  #MT: METRIC FOR FEATURES
  #BB: BACKBONE TO EXTRACT FEATURES
  #BBT: threshold for features
  #JSV: CONSIDER FEATURES JUST FOR SMALL VEHICLES
    (f'{prefixOurData}quantiles_vector_mean_N005_P60_S4_Percentile0.95_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_False', {'BC': 0, 'DLS': 0, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    (f'{prefixOurData}quantiles_vector_mean_N005_P60_S4_Percentile0.95_no_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_True', {'BC': 0, 'DLS': 1, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    (f'{prefixOurData}quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_False', {'BC': 1, 'DLS': 0, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
    (f'{prefixOurData}quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_classic_THR0.25_mindim0__no_features_use_distance_limit_small_True', {'BC': 1, 'DLS': 1, 'FT': 0, 'MT': None, 'BB': None, 'BBT': None, 'JSV': None}),
  ] + dirs_resnet18 + dirs_resnet101 + dirs_vgg11_bn + dirs_vgg19_bn
  specs = (
    [{'BC': 0, 'DLS': 0, 'FT': 0}, {'BC': 0, 'DLS': 1, 'FT': 0}, {'BC': 1, 'DLS': 0, 'FT': 0}, {'BC': 1, 'DLS': 1, 'FT': 0}]
    #[{'BC': 0, 'FT': 0}, {'BC': 1, 'FT': 0}]
    )+specs_resnet18+specs_resnet101+specs_vgg11_bn+specs_vgg19_bn
  header = 'use border correction,use distance limit small,use features,features are just for small vehicles,backbone,metric,threshold,average precision,average recall,average spatial accuracy,allCriticalTPsArePresent,nonzero precision,nonzero recall,nonzero spatial accuracy,total FP,total FN'
  rowTemplate = "{spec.get('BC',null)},{spec.get('DLS',null)},{spec.get('FT',null)},{spec.get('JSV',null)},{spec.get('BB',null)},{spec.get('MT',null)},{spec.get('BBT',null)},{match['precision'].mean()},{match['recall'].mean()},{match['spacc'].mean()},{match['allCriticalTPsArePresent']},{(match['precision']!=0).sum()},{(match['recall']!=0).sum()},{(match['spacc']!=0).sum()},{match['FP'].sum()},{match['FN'].sum()}"
  #header = 'use border correction,use features,features are just for small vehicles,backbone,metric,threshold,average precision,average recall,nonzero precision,nonzero recall'
  #rowTemplate = "{spec.get('BC',null)},{spec.get('FT',null)},{spec.get('JSV',null)},{spec.get('BB',null)},{spec.get('MT',null)},{spec.get('BBT',null)},{match['precision'].mean()},{match['recall'].mean()},{(match['precision']!=0).sum()},{(match['recall']!=0).sum()}"
  return {'prefixpath': prefixpath, 'directories': directories, 'specs': specs, 'header': header, 'rowTemplate': rowTemplate}

def getOtherData():
  prefixpath = '/media/Data/experiments/others/'
  directories = [
    ('quantiles_vector_mean_N005_P60_S4_Percentile0.95_no_border_correction_byte', {'BC': 0, 'AL': 'BYTE', 'BF': 1}),
    ('quantiles_vector_mean_N005_P60_S4_Percentile0.95_no_border_correction_sort', {'BC': 0, 'AL': 'SORT', 'BF': 1}),
    ('quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_byte_BUF1_THR0.25', {'BC': 1, 'AL': 'BYTE', 'BF': 1}),
    ('quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_sort_BUF1_THR0.25', {'BC': 1, 'AL': 'SORT', 'BF': 1}),
    ('quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_byte_BUF5_THR0.25', {'BC': 1, 'AL': 'BYTE', 'BF': 5}),
    ('quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_sort_BUF5_THR_0.25', {'BC': 1, 'AL': 'SORT', 'BF': 5}),
  ]
  specs = [
    {'BC': 0, 'AL': 'BYTE', 'BF': 1},
    {'BC': 1, 'AL': 'BYTE', 'BF': 1},
    {'BC': 1, 'AL': 'BYTE', 'BF': 5},
    {'BC': 0, 'AL': 'SORT', 'BF': 1},
    {'BC': 1, 'AL': 'SORT', 'BF': 1},
    {'BC': 1, 'AL': 'SORT', 'BF': 5},
  ]
  header='use border correction, algorithm, buffer size,average precision,average recall,average spatial accuracy,allCriticalTPsArePresent,nonzero precision,nonzero recall,nonzero spatial accuracy,total FP,total FN'
  rowTemplate = "{spec.get('BC',null)},{spec.get('AL',null)},{spec.get('BF',null)},{match['precision'].mean()},{match['recall'].mean()},{match['spacc'].mean()},{(match['precision']!=0).sum()},{(match['recall']!=0).sum()},{(match['spacc']!=0).sum()},{match['allCriticalTPsArePresent']},{match['FP'].sum()},{match['FN'].sum()}"
  return {'prefixpath': prefixpath, 'directories': directories, 'specs': specs, 'header': header, 'rowTemplate': rowTemplate}
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_no_border_correction_byte
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_no_border_correction_sort
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_byte_BUF1_THR0.25
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_byte_BUF1_THR0.25_mindim0.015
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_byte_BUF1_THR0.25_mindim0.02
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_byte_BUF1_THR0.25_mindim0.025
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_byte_BUF1_THR0.5
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_byte_BUF5_THR0.25
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_byte_BUF5_THR0.25_mindim0.015
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_byte_BUF5_THR0.25_mindim0.02
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_byte_BUF5_THR0.25_mindim0.025
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_byte_BUF5_THR0.5
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_classic_THR0.25
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_classic_THR0.25_mindim0.015
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_classic_THR0.25_mindim0.02
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_classic_THR0.25_mindim0.025
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_classic_THR0.5
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_sort_BUF1_THR0.25
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_sort_BUF1_THR0.25_mindim0.015
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_sort_BUF1_THR0.25_mindim0.02
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_sort_BUF1_THR0.25_mindim0.025
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_sort_BUF1_THR0.5
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_sort_BUF5_THR_0.25
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_sort_BUF5_THR0.25_mindim0.015
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_sort_BUF5_THR0.25_mindim0.02
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_sort_BUF5_THR0.25_mindim0.025
#quantiles_vector_mean_N005_P60_S4_Percentile0.95_with_border_correction_sort_BUF5_THR0.5

def guarrada(summaries):
  thrs = (0.1,0.2,0.3,0.4,0.5)
  specsToShow1 = [{'BC': 0, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': 'resnet18', 'BBT': x, 'JSV': 0} for x in thrs]
  specsToShow2 = [{'BC': 1, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': 'resnet18', 'BBT': x, 'JSV': 0} for x in thrs]
  specsToShow3 = [{'BC': 0, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': 'resnet18', 'BBT': x, 'JSV': 1} for x in thrs]
  specsToShow4 = [{'BC': 1, 'DLS': 1, 'FT': 1, 'MT': 'cos', 'BB': 'resnet18', 'BBT': x, 'JSV': 1} for x in thrs]
  allSpecsToShow = (specsToShow1, specsToShow2, specsToShow3, specsToShow4)
  measureNamesA = ('precision', 'recall')
  xyssA = [getCurves(summaries, specsToShow, 'BBT', measureNamesA, [np.mean]*2) for specsToShow in allSpecsToShow]
  everythingA = []
  for xs, yss in xyssA:
    for ys in yss:
      everythingA.append(xs)
      everythingA.append(ys)
  measureNamesB = ('FP', 'FN')
  xyssB = [getCurves(summaries, specsToShow, 'BBT', measureNamesB, [np.sum]*2) for specsToShow in allSpecsToShow]
  everythingB = []
  for xs, yss in xyssB:
    for ys in yss:
      everythingB.append(xs)
      everythingB.append(ys)
      everythingB.append('--')
  allMeasureNamesA = []
  for specsToShow in allSpecsToShow:
    for mn in measureNamesA:
      allMeasureNamesA.append(f'{mn}; BC={specsToShow[0]["BC"]}; JSV={specsToShow[0]["JSV"]}')
  allMeasureNamesB = []
  for specsToShow in allSpecsToShow:
    for mn in measureNamesB:
      allMeasureNamesB.append(f'{mn}; BC={specsToShow[0]["BC"]}; JSV={specsToShow[0]["JSV"]}')
  fig, axs = plt.subplots(1, 1)
  axs.plot(*everythingA)
  ax2 = axs.twinx()
  ax2.plot(*everythingB)
  axs.legend(allMeasureNamesA)
  ax2.legend(allMeasureNamesB)
  plt.show()

if __name__=='__main__':
  basedata = getBaseData()
  summaries = writeAllSummaries(**basedata)
  writeTable(os.path.join(basedata['prefixpath'], 'spatialAcc.csv'), summaries, 'spacc')
  writeTable(os.path.join(basedata['prefixpath'], 'precision.csv'), summaries, 'precision')
  summaries = writeAllSummaries(**getOurData())
  #guarrada(summaries)
  
  writeAllSummaries(**getOtherData())


