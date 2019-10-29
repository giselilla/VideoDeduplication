from glob import glob
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from winnow.feature_extraction import SimilarityModel
import cv2
import yaml

print('Loading config file')


with open("config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)


representations = ['frame_level','video_level','video_signatures']
    
DST_DIR = cfg['destination_folder']
ROOT_FOLDER_INTERMEDIATE_REPRESENTATION =cfg['root_folder_intermediate']
VIDEO_SIGNATURES_SAVE_FOLDER = cfg['video_signatures_folder'] 
DISTANCE = float(cfg['match_distance'])
MIN_VIDEO_DURATION = float(cfg['min_video_duration_seconds'])
HANDLE_DARK = str(cfg['filter_dark_videos'])
DARK_THR = float(cfg['filter_dark_videos_thr'])
DST_FOLDER = cfg['destination_folder']
VIDEO_LEVEL_SAVE_FOLDER = cfg['video_level_folder']
FRAME_LEVEL_SAVE_FOLDER = os.path.abspath(DST_DIR +
                                          '{}/{}'.format(ROOT_FOLDER_INTERMEDIATE_REPRESENTATION,representations[0]))



def extract_additional_info(x):
    
    v = np.load(x)
    frames = np.load(x.replace('_vgg_features','_vgg_frames'))
    grays = np.array([cv2.cvtColor(x,cv2.COLOR_BGR2GRAY) for x in frames])
    grays = np.array([np.mean(x) for x in grays])

    grays_avg = np.mean(grays,axis=0)
    grays_std = np.std(grays,axis=0)
    try:
        grays_max = np.max(grays)
    except:
        grays_max = 0

    shape = v.shape
    intra_sum = np.sum(v,axis=1)
    mean_act = np.mean(intra_sum)
    try:
        
        max_dif = np.max(intra_sum) - np.min(intra_sum)
        
    except:
        max_dif = 0
    std_sum = np.std(intra_sum)
    
    return shape[0],mean_act,std_sum,max_dif,grays_avg,grays_std,grays_max



print('Extracting Video Signatures')
sm = SimilarityModel()
video_signatures = sm.predict(VIDEO_LEVEL_SAVE_FOLDER)
video_signatures = np.nan_to_num(video_signatures)
labels = np.array([x.split('_vgg')[0].split('/')[-1] for x in  sm.index])


def filter_results(thr):
    results = []
    results_distances = []
    msk = distances < thr
    for i,r in enumerate(msk):
        results.append(indices[i,r])
        results_distances.append(distances[i,r])
    return results,results_distances

def uniq(row):
    
    return ''.join([str(x) for x in sorted([row['query'],row['match']])])



print('Finding Matches...')
nn = NearestNeighbors(n_neighbors=20,metric='euclidean',algorithm='kd_tree')
nn.fit(video_signatures)
distances,indices = nn.kneighbors(video_signatures)


results,results_distances = filter_results(DISTANCE)

ss = sorted(zip(results,results_distances),key=lambda x:len(x[0]),reverse=True)
results_sorted = [x[0] for x in ss]
results_sorted_distance = [x[1] for x in ss]


q = []
m = []
distance = []

print('Generating Report')
for i,r in enumerate(results_sorted):
    for j,matches in enumerate(r):
        if j == 0:
            qq = matches
        q.append(qq)
        m.append(matches)
        distance.append(results_sorted_distance[i][j])

match_df = pd.DataFrame({"query":q,"match":m,"distance":distance})            
match_df['query_video'] = labels[match_df['query']]
match_df['match_video'] = labels[match_df['match']]
match_df['self_match'] = match_df['query_video'] == match_df['match_video']
# Remove self matches
match_df = match_df.loc[~match_df['self_match'],:]
# Creates unique index from query, match 
match_df['unique_index'] = match_df.apply(uniq,axis=1)
# Removes duplicated entries (eg if A matches B, we don't need B matches A)
match_df = match_df.drop_duplicates(subset=['unique_index'])


REPORT_PATH = DST_FOLDER + '/matches_at_{}_distance.csv'.format(DISTANCE)

print('Saving unfiltered report to {}'.format(REPORT_PATH))

match_df.to_csv(REPORT_PATH)




if HANDLE_DARK == 'True':
    
    print('Filtering dark and/or short videos')

    frame_level_repres = glob(FRAME_LEVEL_SAVE_FOLDER + '/**_features.npy')
    frame_level_data = np.array([extract_additional_info(x) for x in frame_level_repres])

    video_length = np.array(frame_level_data)[:,0]
    video_avg_act = frame_level_data[:,1]
    video_avg_mean = frame_level_data[:,2]
    video_avg_max_dif = frame_level_data[:,3]
    gray_avg = frame_level_data[:,4]
    gray_std = frame_level_data[:,5]
    gray_max = frame_level_data[:,6]


    metadata_df = pd.DataFrame({'frame_level_fn':frame_level_repres,
                                "video_length":video_length,
                                "avg_act":video_avg_act,
                                "video_avg_std":video_avg_mean,
                                "video_max_dif":video_avg_max_dif,
                                "gray_avg":gray_avg,
                                "gray_std":gray_std,
                                "gray_max":gray_max})

    metadata_df['fn'] = metadata_df['frame_level_fn'].apply(lambda x:x.split('/')[-1].split('_vgg_features')[0])


    sign = pd.DataFrame(dict(features_fn=sm.index))
    sign['fn'] = sign['features_fn'].apply(lambda x:x.split('/')[-1].split('_vgg_features')[0])
    merged = sign.merge(metadata_df,on='fn')
    merged['video_frames_fn'] = merged['frame_level_fn'].apply(lambda x : x.replace('_vgg_features','_vgg_frames'))
    merged['video_duration_flag'] = merged.video_length < MIN_VIDEO_DURATION
    
    print('Videos discarded because of duration:{}'.format(merged['video_duration_flag'].sum()))
    
    merged['video_dark_flag'] = merged.gray_max < DARK_THR
    
    print('Videos discarded because of darkness:{}'.format(merged['video_dark_flag'].sum()))
    
    merged['flagged'] = merged['video_dark_flag'] | merged['video_duration_flag']
    discarded_videos = merged.loc[merged['flagged'],:]['fn']
    msk_1 = match_df['query_video'].isin(discarded_videos)
    msk_2 = match_df['match_video'].isin(discarded_videos)
    discard_msk = msk_1 | msk_2
    
    FILTERED_REPORT_PATH = DST_FOLDER + '/matches_at_{}_distance_filtered.csv'.format(DISTANCE)
    METADATA_REPORT_PATH = DST_FOLDER + '/metadata_signatures.csv'
    
    filtered_match_df = match_df.loc[~discard_msk,:]
    filtered_match_df.to_csv(FILTERED_REPORT_PATH)
    print('Saving filtered report to {}'.format(FILTERED_REPORT_PATH))
    print('Saving metadata to {}'.format(METADATA_REPORT_PATH))
    merged.to_csv(METADATA_REPORT_PATH)