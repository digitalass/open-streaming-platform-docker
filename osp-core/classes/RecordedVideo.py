from .shared import db
from uuid import uuid4

from functions import cachedDbCalls

import os
from globals import globalvars


class RecordedVideo(db.Model):
    __tablename__ = "RecordedVideo"
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255))
    videoDate = db.Column(db.DateTime)
    owningUser = db.Column(db.Integer, db.ForeignKey("user.id"))
    channelName = db.Column(db.String(255))
    channelID = db.Column(db.Integer, db.ForeignKey("Channel.id"))
    description = db.Column(db.String(4096))
    topic = db.Column(db.Integer)
    views = db.Column(db.Integer)
    length = db.Column(db.Float)
    videoLocation = db.Column(db.String(255))
    thumbnailLocation = db.Column(db.String(255))
    gifLocation = db.Column(db.String(255))
    pending = db.Column(db.Boolean)
    allowComments = db.Column(db.Boolean)
    published = db.Column(db.Boolean)
    originalStreamID = db.Column(db.Integer)
    upvotes = db.relationship(
        "videoUpvotes",
        backref="recordedVideo",
        cascade="all, delete-orphan",
        lazy="noload",
    )
    comments = db.relationship(
        "videoComments",
        backref="recordedVideo",
        cascade="all, delete-orphan",
        lazy="noload",
    )
    clips = db.relationship(
        "Clips", backref="recordedVideo", lazy="noload"
    )
    tags = db.relationship(
        "video_tags",
        backref="recordedVideo",
        cascade="all, delete-orphan",
        lazy="noload",
    )

    def __init__(
        self,
        owningUser,
        channelID,
        channelName,
        topic,
        views,
        videoLocation,
        videoDate,
        allowComments,
        published,
    ):
        self.uuid = str(uuid4())
        self.videoDate = videoDate
        self.owningUser = owningUser
        self.channelID = channelID
        self.channelName = channelName
        self.topic = topic
        self.views = views
        self.videoLocation = videoLocation
        self.pending = True
        self.published = published
        self.allowComments = allowComments

    def __repr__(self):
        return "<id %r>" % self.id

    def get_video_exists(self):
        videos_root = globalvars.videoRoot + "videos/"
        filePath = videos_root + self.videoLocation

        if filePath != videos_root:
            if os.path.exists(filePath):
                return True
        return False

    def get_upvotes(self):
        return cachedDbCalls.getVideoUpvotes(self.id)
    
    def get_clips(self):
        return cachedDbCalls.getClipsForVideo(self.id)

    def get_tags(self):
        return cachedDbCalls.getVideoTags(self.id)

    def serialize(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "channelID": self.channelID,
            "owningUser": self.owningUser,
            "videoDate": str(self.videoDate),
            "videoName": self.channelName,
            "description": self.description,
            "topic": self.topic,
            "views": self.views,
            "length": self.length,
            "upvotes": self.get_upvotes(),
            "videoLocation": "/videos/" + self.videoLocation,
            "thumbnailLocation": "/videos/" + self.thumbnailLocation,
            "gifLocation": "/videos/" + self.gifLocation,
            "ClipIDs": [obj.id for obj in self.get_clips()],
            "tags": [obj.id for obj in self.get_tags()],
        }

    def remove(self):
        videos_root = globalvars.videoRoot + "videos/"

        filePath = videos_root + self.videoLocation
        thumbnailPath = videos_root + self.videoLocation[:-4] + ".png"
        gifLocation = videos_root + self.videoLocation[:-4] + ".gif"

        if filePath != videos_root:
            if os.path.exists(filePath) and (
                self.videoLocation is not None or self.videoLocation != ""
            ):
                os.remove(filePath)
                if os.path.exists(thumbnailPath):
                    os.remove(thumbnailPath)
                if os.path.exists(gifLocation):
                    os.remove(gifLocation)


class video_tags(db.Model):
    __tablename__ = "video_tags"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    videoID = db.Column(db.Integer, db.ForeignKey("RecordedVideo.id"))
    taggedByUser = db.Column(db.Integer)

    def __init__(self, tagName, videoID, userID):
        self.name = tagName
        self.videoID = videoID
        self.taggedByUser = userID

    def __repr__(self):
        return "<id %r>" % self.id


class Clips(db.Model):
    __tablename__ = "Clips"
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255))
    clipDate = db.Column(db.DateTime)
    owningUser = db.Column(db.Integer, db.ForeignKey("user.id", name="clips_owningUser_to_userid", ondelete="CASCADE"))
    channelID = db.Column(db.Integer, db.ForeignKey("Channel.id", name="clips_channelID_to_channelid", ondelete="CASCADE"))
    parentVideo = db.Column(db.Integer, db.ForeignKey("RecordedVideo.id", name="clips_parentVideo_to_RecordedVideoid", ondelete="SET NULL"))
    startTime = db.Column(db.Float)
    endTime = db.Column(db.Float)
    length = db.Column(db.Float)
    views = db.Column(db.Integer)
    clipName = db.Column(db.String(255))
    videoLocation = db.Column(db.String(255))
    description = db.Column(db.String(2048))
    topic = db.Column(db.Integer)
    thumbnailLocation = db.Column(db.String(255))
    gifLocation = db.Column(db.String(255))
    published = db.Column(db.Boolean)
    upvotes = db.relationship(
        "clipUpvotes", backref="clip", cascade="all, delete-orphan", lazy="joined"
    )
    tags = db.relationship(
        "clip_tags", backref="clip", cascade="all, delete-orphan", lazy="joined"
    )

    def __init__(
        self, clipDate, parentVideoQuery, videoLocation, startTime, endTime, clipName, description
    ):
        self.uuid = str(uuid4())
        self.clipDate = clipDate
        self.parentVideo = parentVideoQuery.id
        self.owningUser = parentVideoQuery.owningUser
        self.channelID = parentVideoQuery.channelID
        self.videoLocation = videoLocation
        self.startTime = startTime
        self.endTime = endTime
        self.description = description
        self.topic = parentVideoQuery.topic
        self.clipName = clipName
        self.length = endTime - startTime
        self.views = 0
        self.published = True

    def __repr__(self):
        return "<id %r>" % self.id

    def serialize(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "clipDate": str(self.clipDate),
            "parentVideo": self.parentVideo,
            "owningUser": self.owningUser,
            "channelID": self.channelID,
            "startTime": self.startTime,
            "endTime": self.endTime,
            "length": self.length,
            "name": self.clipName,
            "description": self.description,
            "topic": self.topic,
            "views": self.views,
            "videoLocation": "/videos/" + self.videoLocation,
            "thumbnailLocation": "/videos/" + self.thumbnailLocation,
            "gifLocation": "/videos/" + self.gifLocation,
        }

    def remove(self):
        videos_root = globalvars.videoRoot + "videos/"

        filePath = videos_root + self.videoLocation
        thumbnailPath = videos_root + self.videoLocation[:-4] + ".png"
        gifLocation = videos_root + self.videoLocation[:-4] + ".gif"

        if filePath != videos_root:
            if os.path.exists(filePath) and (
                self.videoLocation is not None or self.videoLocation != ""
            ):
                os.remove(filePath)
                if os.path.exists(thumbnailPath):
                    os.remove(thumbnailPath)
                if os.path.exists(gifLocation):
                    os.remove(gifLocation)


class clip_tags(db.Model):
    __tablename__ = "clip_tags"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    clipID = db.Column(db.Integer, db.ForeignKey("Clips.id"))
    taggedByUser = db.Column(db.Integer)

    def __init__(self, tagName, clipID, userID):
        self.name = tagName
        self.clipID = clipID
        self.taggedByUser = userID

    def __repr__(self):
        return "<id %r>" % self.id
