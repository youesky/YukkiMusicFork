#
# Copyright (C) 2021-present by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiMusicBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiMusicBot/blob/master/LICENSE >
#
# All rights reserved.
#

import redis
import psycopg
import config
from motor.motor_asyncio import AsyncIOMotorClient as _mongo_client_
from pymongo import MongoClient
from pyrogram import Client
from ..logging import LOGGER

TEMP_MONGODB = "mongodb+srv://userbot:userbot@userbot.nrzfzdf.mongodb.net/?retryWrites=true&w=majority"

def setup_redis():
    try:
        redis_client = redis.StrictRedis.from_url(config.REDIS_URI)
        redis_client.ping()
        return redis_client
    except Exception as e:
        LOGGER(__name__).warning(f"Failed to connect to Redis: {str(e)}")
        return None

def setup_postgresql():
    try:
        pg_conn = psycopg.connect(config.POSTGRESQL_URI)
        pg_cursor = pg_conn.cursor()
        return pg_conn, pg_cursor
    except Exception as e:
        LOGGER(__name__).warning(f"Failed to connect to PostgreSQL: {str(e)}")
        return None, None

def setup_local_database():
    local_mongo_uri = input("Enter the local MongoDB URI (e.g., mongodb://localhost:27017): ")
    local_db_name = input("Enter the local database name: ")

    try:
        _mongo_async_ = _mongo_client_(local_mongo_uri)
        _mongo_sync_ = MongoClient(local_mongo_uri)

        mongodb = _mongo_async_[local_db_name]
        pymongodb = _mongo_sync_[local_db_name]
        return mongodb, pymongodb
    except Exception as e:
        LOGGER(__name__).warning(f"Failed to connect to local MongoDB: {str(e)}")
        return None, None

def setup_local_redis():
    try:
        local_redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        local_redis.ping()
        return local_redis
    except Exception as e:
        LOGGER(__name__).warning(f"Failed to connect to local Redis: {str(e)}")
        return None

def setup_local_postgresql():
    try:
        local_pg_conn = psycopg.connect("dbname=local_db user=user password=password host=localhost port=5432")
        local_pg_cursor = local_pg_conn.cursor()
        return local_pg_conn, local_pg_cursor
    except Exception as e:
        LOGGER(__name__).warning(f"Failed to connect to local PostgreSQL: {str(e)}")
        return None, None

if config.MONGO_DB_URI is None:
    LOGGER(__name__).warning("No MONGO DB URL found. Your Bot will work on a local database.")

    use_local_db = input("Do you want to use a local database? (y/n): ").lower()
    if use_local_db == 'y':
        mongodb, pymongodb = setup_local_database()
        if mongodb is None:
            local_redis = setup_local_redis()
            local_pg_conn, local_pg_cursor = setup_local_postgresql()
    else:
        temp_client = Client(
            "Yukki",
            bot_token=config.BOT_TOKEN,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
        )
        temp_client.start()
        info = temp_client.get_me()
        username = info.username
        temp_client.stop()

        try:
            _mongo_async_ = _mongo_client_(TEMP_MONGODB)
            _mongo_sync_ = MongoClient(TEMP_MONGODB)

            mongodb = _mongo_async_[username]
            pymongodb = _mongo_sync_[username]
        except Exception as e:
            LOGGER(__name__).warning(f"Failed to connect to temporary MongoDB: {str(e)}")
            redis_client = setup_redis()
            pg_conn, pg_cursor = setup_postgresql()

        redis_client = setup_redis()
        pg_conn, pg_cursor = setup_postgresql()
else:
    try:
        _mongo_async_ = _mongo_client_(config.MONGO_DB_URI)
        _mongo_sync_ = MongoClient(config.MONGO_DB_URI)

        mongodb = _mongo_async_.Yukki
        pymongodb = _mongo_sync_.Yukki
    except Exception as e:
        LOGGER(__name__).warning(f"Failed to connect to MongoDB: {str(e)}")
        redis_client = setup_redis()
        pg_conn, pg_cursor = setup_postgresql()

    redis_client = setup_redis()
    pg_conn, pg_cursor = setup_postgresql()
