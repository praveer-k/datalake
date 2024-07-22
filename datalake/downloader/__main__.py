from datalake.downloader.yelp_dataset import YelpDataset

def main():
    yd = YelpDataset()
    signed_url = yd.get_signed_url()
    yd.download(signed_url).extract()
