import os
import httpx
import tarfile
from tqdm import tqdm
from typing import Self
from bs4 import BeautifulSoup
from datalake.config import settings, logger

class YelpDataset:
    def __init__(self):
        self.download_link = settings.YELP_DATASET.DOWNLOAD_LINK
        self.download_filename = os.path.relpath(settings.YELP_DATASET.LOCAL_PATH.rstrip('/\\') + '.tar')
        self.extraction_path = os.path.relpath(settings.YELP_DATASET.LOCAL_PATH)
        os.makedirs(self.extraction_path, exist_ok=True)
        logger.info(f'Yelp dataset download link: {self.download_link}')

    def get_signed_url(self):
        with httpx.Client() as client:
            login_page = client.get(self.download_link)
            login_page_soup = BeautifulSoup(login_page.text, 'html.parser')
            csrftok = login_page_soup.find('input', {'name': 'csrftok'})['value']
            payload = {
                'csrftok': csrftok,
                'name': settings.YELP_DATASET.AUTH.NAME,
                'email': settings.YELP_DATASET.AUTH.EMAIL,
                'signature': settings.YELP_DATASET.AUTH.SIGNATURE,
                'terms_accepted': 'y'
            }
            login_response = client.post(self.download_link, data=payload)
            if login_response.status_code == 200:
                logger.info("Log in successfully")
                dataset_page_soup = BeautifulSoup(login_response.text, 'html.parser')
                signed_url = dataset_page_soup.find('a', text='Download JSON')['href']
                return signed_url
            else:
                logger.error(f"Failed to log in. Status code: {login_response.status_code}")
                raise httpx.HTTPError("Login failed !!!")

    def download(self, download_link) -> Self:
        try:
            with open(self.download_filename, 'wb') as file:
                with httpx.stream("GET", download_link) as response:
                    response.raise_for_status()
                    total = int(response.headers["Content-Length"])
                    with tqdm(total=total, unit_scale=True, unit_divisor=1024, unit="B") as progress:
                        num_bytes_downloaded = response.num_bytes_downloaded
                        for chunk in response.iter_bytes():
                            file.write(chunk)
                            progress.update(response.num_bytes_downloaded - num_bytes_downloaded)
                            num_bytes_downloaded = response.num_bytes_downloaded
                logger.info(f"Downloaded dataset from {download_link} to {self.download_filename}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise
        except httpx.RequestError as e:
            logger.error(f"An error occurred while requesting {e.request.url!r}.")
            raise
        except IOError as e:
            logger.error(f"An IO error occurred: {e}")
        return self
    
    def extract(self):
        with tarfile.open(self.download_filename, 'r') as tar:
            logger.info(f"Extracting {self.download_filename} to {self.extraction_path}...")
            tar.extractall(path=self.extraction_path)
            logger.info("Extraction complete.")
