import os
import sys
import grpc
import logging
import instaloader
import Instagram_pb2
import Instagram_pb2_grpc

from concurrent import futures
from pymongo import MongoClient


class DownloadInstagramPostServicer(Instagram_pb2_grpc.DownloadInstagramPostServicer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("grpc server")
        self.logger.setLevel(logging.INFO)  # Do not allow DEBUG messages through
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("{asctime}: {levelname}: {name}: {message}", style="{")
        )
        self.logger.addHandler(handler)
        self.logger.info("Starting...")

    def Download(self, request, context):
        guild = request.guild
        URL   = request.url
        #state = request.state
        print("We made it??")
        self.logger.info("Call received.")
        # look up the post download document 
        client = MongoClient("mongodb://192.168.1.107:27017/")
        job = client.Monty.downloader.find_one({"server": guild, "URL": URL})
        print("We made it??")
        self.logger.info(job)
        self.logger.info(f"{guild}. {URL}")
        if not job:
            self.logger.error("No job found")
            return Instagram_pb2.InstagramResponse(success=False)
        query_filter = {"URL": URL, "server": guild}
        summarize = job["summarize"]
        self.logger.info(f"starting thread for {URL}")
        file_path = job["path"]
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        _ = client.Monty.downloader.find({"server": guild, "URL": URL})[0]
        self.update_job_state(client, query_filter, "Insta-Started")
        loader = instaloader.Instaloader(
            download_comments=False,
            download_geotags=False,
            download_video_thumbnails=False,
            save_metadata=False,
            dirname_pattern=file_path,
            post_metadata_txt_pattern="",
        )
        shortcode = URL.split("/")[-2]
        try:
            # download post
            post = instaloader.Post.from_shortcode(loader.context, shortcode)
            if summarize and not post.is_video:
                self.logger.info(
                    "Pictures cannot be summarized from this workflow. No summary returned."
                )
                summarize = False
            if summarize and post.video_duration > 180:
                self.logger.error("Video too long for a summary. Not providing one.")
                summarize = False
            loader.download_post(post, target=shortcode)

        except Exception as e:
            self.logger.error(f"Something went wrong: {e}")
            reason = f"Error in download:{e}"
            self.update_job_state(client, query_filter, "Failed.", True, reason)
            return Instagram_pb2.InstagramResponse(success=False)
        # update mongodb document
        the_file = os.listdir(file_path)
        update = {
            "$set": {
                "state": "Downloaded",
                "file": the_file,
                "path": file_path,
                "summarize": summarize,
            }
        }
        client.Monty.downloader.update_one(query_filter, update)
        # return result
        return Instagram_pb2.InstagramResponse(success=True)
    
    def update_job_state(self, client, query_filter, state, failed=False, reason=None):
        self.logger.info(f"state updated to :{state}")
        update = {"$set": {"state": state}}
        client.Monty.downloader.update_one(query_filter, update)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Instagram_pb2_grpc.add_DownloadInstagramPostServicer_to_server(DownloadInstagramPostServicer(), server)
    server.add_insecure_port('[::]:5103')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
