from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine,Table, Column, String, MetaData,Integer,Binary,Boolean,Float,ARRAY,JSON


Base = declarative_base()

class Signature(Base):
    
    __tablename__ = 'signatures'
    id = Column(Integer,primary_key=True)
    original_filename = Column(String)
    signature = Column(Binary)

# TODO:Revaluate which columns are actually essential
# TODO: Add sha signature

class VideoMetadata(Base):
    
    __tablename__ = 'videometadata'

    original_filename = Column(String,primary_key=True)
    video_length = Column(Float)
    avg_act = Column(Float)
    video_avg_std = Column(Float)
    video_max_dif = Column(Float)
    gray_avg = Column(Float)
    gray_std = Column(Float)
    gray_max = Column(Float)
    gray_max = Column(Float)
    video_duration_flag = Column(Boolean)
    video_dark_flag = Column(Boolean)
    flagged = Column(Boolean)
    

class Scenes(Base):

    __tablename__ = 'scenes'
    original_filename = Column(String,primary_key=True)
    video_duration_seconds = Column(Float)
    avg_duration_seconds = Column(Float)
    scene_duration_seconds = Column(ARRAY(Integer))
    scenes_timestamp = Column(ARRAY(String))
    total_video_duration_timestamp = Column(String)


class Matches(Base):

    __tablename__ = 'matches'
    id = Column(Integer, primary_key = True) 
    query_video = Column(String)
    match_video = Column(String)
    distance = Column(Float)


class Exif(Base):

    __tablename__ = 'exif'
    original_filename = Column(String,primary_key=True)
    General_FileName = Column(String,primary_key=True)
    General_FileExtension = Column(String)
    General_Format_Commercial = Column(String)
    General_FileSize = Column(Float)
    General_Duration = Column(Float)
    General_OverallBitRate_Mode = Column(String)
    General_OverallBitRate = Column(Float)
    General_FrameRate = Column(Float)
    General_FrameCount = Column(Float)
    General_Encoded_Date = Column(String)
    General_File_Modified_Date = Column(String)
    General_File_Modified_Date_Local = Column(String)
    General_Tagged_Date = Column(String)
    Video_Format = Column(String)
    Video_BitRate = Column(Float)
    Video_InternetMediaType = Column(String)
    Video_Width = Column(Float)
    Video_Height = Column(Float)
    Video_FrameRate = Column(Float)
    Audio_Format = Column(String)
    Audio_SamplingRate = Column(Float)
    Audio_Title = Column(String)
    Audio_BitRate = Column(Float)
    Audio_Channels = Column(Float)
    Audio_Duration = Column(Float)
    Audio_Encoded_Date = Column(String)
    Audio_Tagged_Date = Column(String)
    Json_full_exif = Column(JSON)





