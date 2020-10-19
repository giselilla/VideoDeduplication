import json

import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from winnow.utils import get_hash
from .schema import Files, Signature, Scene, VideoMetadata, Matches, Exif, Base, Templatematches


# TODO: Migrate to winnow.storage.db_result_storage API.
# TODO: Move db.Database here.

def create_engine_session(conn_string):
    """Creates DB engine from connection string
    
    Arguments:
        conn_string {string} -- Connection string with format postgres://postgres:[USER]:[PASSWORD]@[HOST]:[PORT]/[DBNAME]

        eg. postgres://postgres:admin@localhost:5432/test
    """

    db_engine = create_engine(conn_string)
    Session = sessionmaker(bind=db_engine)
    session = Session()

    return db_engine, session


# Initial table creation / deletion
def create_tables(engine):
    """Creates all tables specified on our internal schema
    
    Arguments:
        engine {SQL Alchemy DB Engine instance} -- Instance of SQL Alchemy DB session
    """
    Base.metadata.create_all(engine)


def delete_tables(engine):
    """Drop database"""
    Base.metadata.drop_all(engine)


# Bulk loading the original output into target tables

def add_scenes(session, scenes):
    """Bulk add scenes to DB
    
    Arguments:
        session {DB Session} -- created by a previous instantiation of the db session
        scenes {pd.Dataframe} -- Pandas Dataframe containing scene information 
    """
    for _, row in scenes.iterrows():
        start_time = 0
        for duration in row['scene_duration_seconds']:
            session.add(Scene(file_id=row['file_id'], start_time=start_time * 1000, duration=duration * 1000))
            start_time += duration


def load_scenes(session, scenes_df_path):
    """Loads scene information into the scenes DB table
    
    Arguments:
        session {DB Session} -- created by a previous instantiation of the db session
        scenes_df_path {string} -- Path to the scenes detection output (csv file)
    """

    df = pd.read_csv(scenes_df_path)

    add_scenes(session, df)


def add_files(session, file_paths):
    hashes = [get_hash(fp) for fp in file_paths]
    session.add_all([Files(sha256=x[0],
                           file_path=x[1]) for x in zip(list(hashes), list(file_paths))])

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        print('DB Exception', e)
    finally:
        # Get DB stats
        files = get_all(session, Files)
        print(f"Files table rows:{len(files)}")
        return files


def add_signatures(session, signatures, file_ids):
    """Bulk add Signatures to db
    
    Arguments:
        signatures {np.array} -- Numpy array containing signatures extracted by job
        filenames {np.array} -- Filename index
    """
    session.add_all([Signature(file_id=x[0],
                               signature=x[1]) for x in zip(list(file_ids), list(signatures))])

    try:
        session.commit()

    except Exception as e:
        session.rollback()
        print('DB Exception', e)
    finally:
        # Get DB stats
        signatures = get_all(session, Signature)
        print(f"Signatures table rows:{len(signatures)}")
        return signatures


def load_signatures(session, signatures_fp, signatures_index):
    """Load signatures into DB
    
    Arguments:
        session {DB Session} -- created by a previous instantiation
        signatures_fp {string} -- path to generated signatures
        signatures_index {string} -- path to the index of generated signatures
    """

    signatures = np.load(signatures_fp)
    filenames = np.load(signatures_index)

    print(signatures.shape)
    print(filenames.shape)

    add_signatures(session, signatures, filenames)


def add_metadata(session, metadata):
    """Bulk add metadata to DB
    
    Arguments:
        session {[DB Session]} -- Current DB Session (generated by SQL Alchemy create session)
        metadata {[pd.DataFrame]} -- Dataframe with generated Metadata 
    """

    session.add_all([VideoMetadata(
        file_id=x['file_id'],
        video_length=x['video_length'],
        avg_act=x['avg_act'],
        video_avg_std=x['video_avg_std'],
        video_max_dif=x['video_max_dif'],
        gray_avg=x['gray_avg'],
        gray_std=x['gray_std'],
        gray_max=x['gray_max'],
        video_dark_flag=x['video_dark_flag'],
        video_duration_flag=x['video_duration_flag'],
        flagged=x['flagged']

    ) for i, x in metadata.iterrows()])


def add_matches(session, matches):
    session.add_all([Matches(
        query_video=x['query_video'],
        query_video_file_id=x['query_video_file_id'],
        match_video=x['match_video'],
        match_video_file_id=x['match_video_file_id'],
        distance=x['distance']
    ) for i, x in matches.iterrows()])


def load_metadata(session, metadata_df_path):
    """Loads video metadata into DB (video metadata table)
    
    Arguments:
        session {DB Session} -- created by a previous instantiation
        scenes_df_path {string} -- Path to the video metadataoutput (csv file)
    """

    df = pd.read_csv(metadata_df_path)

    add_metadata(session, df)


# DB Queries

def load_matches(session, matches_df_path):
    """Loads video metadata into DB (video metadata table)
    
    Arguments:
        session {DB Session} -- created by a previous instantiation
        matches_df_path {string} -- Path to the matches (csv file)
    """
    df = pd.read_csv(matches_df_path)

    add_matches(session, df)


def add_exif(session, exif_df, json_list):
    COLUMNS_OF_INTEREST = [
        'General_FileName',
        'General_FileExtension',
        'General_Format_Commercial',
        'General_FileSize',
        'General_Duration',
        'General_OverallBitRate_Mode',
        'General_OverallBitRate',
        'General_FrameRate',
        'General_FrameCount',
        'General_Encoded_Date',
        'General_File_Modified_Date',
        'General_File_Modified_Date_Local',
        'General_Tagged_Date',
        'Video_Format',
        'Video_BitRate',
        'Video_InternetMediaType',
        'Video_Width',
        'Video_Height',
        'Video_FrameRate',
        'Audio_Format',
        'Audio_SamplingRate',
        'Audio_Title',
        'Audio_BitRate',
        'Audio_Channels',
        'Audio_Duration',
        'Audio_Encoded_Date',
        'Audio_Tagged_Date']

    # Results from mediainfo might be inconsistent. So we need to add columns for every expected field (even if there is no info)
    for col in COLUMNS_OF_INTEREST:

        if col not in exif_df.columns:
            exif_df[col] = None

    session.add_all([Exif(file_id=x['file_id'],
                          General_FileSize=x["General_FileSize"],
                          General_FileExtension=x["General_FileExtension"],
                          General_Format_Commercial=x["General_Format_Commercial"],
                          General_Duration=x["General_Duration"],
                          General_OverallBitRate_Mode=x["General_OverallBitRate_Mode"],
                          General_OverallBitRate=x["General_OverallBitRate"],
                          General_FrameRate=x["General_FrameRate"],
                          General_FrameCount=x["General_FrameCount"],
                          General_Encoded_Date=x["General_Encoded_Date"],
                          General_File_Modified_Date=x["General_File_Modified_Date"],
                          General_File_Modified_Date_Local=x["General_File_Modified_Date_Local"],
                          General_Tagged_Date=x["General_Tagged_Date"],
                          Video_Format=x["Video_Format"],
                          Video_BitRate=x["Video_BitRate"],
                          Video_InternetMediaType=x["Video_InternetMediaType"],
                          Video_Width=x["Video_Width"],
                          Video_Height=x["Video_Height"],
                          Video_FrameRate=x["Video_FrameRate"],
                          Audio_Format=x["Audio_Format"],
                          Audio_SamplingRate=x["Audio_SamplingRate"],
                          Audio_Title=x["Audio_Title"],
                          Audio_BitRate=x["Audio_BitRate"],
                          Audio_Channels=x["Audio_Channels"],
                          Audio_Duration=x["Audio_Duration"],
                          Audio_Encoded_Date=x["Audio_Encoded_Date"],
                          Audio_Tagged_Date=x["Audio_Tagged_Date"],
                          Json_full_exif=json.dumps(json_list[i])
                          ) for i, x in exif_df.iterrows()])
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        print('DB Exception', e)

    finally:
        # Get DB stats
        exif_rows = get_all(session, Exif)
        return exif_rows

        print(f"Exif table rows:{len(exif_rows)}")


def get_all(session, instance):
    query = session.query(instance)
    return query.all()

