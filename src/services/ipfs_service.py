import requests
import logging
from config.config import settings

logger = logging.getLogger(__name__)

class IPFSService:
    def __init__(self):
        self.api_key = settings.PINATA_API_KEY
        self.api_secret = settings.PINATA_API_SECRET
        self.jwt = settings.PINATA_JWT
        self.base_url = "https://api.pinata.cloud"

    def upload_file(self, file_content, filename):
        """
        Uploads file to Pinata IPFS and returns the CID.
        """
        url = f"{self.base_url}/pinning/pinFileToIPFS"
        
        headers = {
            'Authorization': f'Bearer {self.jwt}'
        }

        files = {
            'file': (filename, file_content)
        }

        try:
            logger.info(f"Uploading {filename} to Pinata...")
            response = requests.post(url, files=files, headers=headers)
            response.raise_for_status()
            data = response.json()
            cid = data['IpfsHash']
            logger.info(f"Successfully uploaded to IPFS. CID: {cid}")
            return cid
        except Exception as e:
            logger.error(f"IPFS upload failed: {e}")
            raise Exception(f"Failed to upload to IPFS: {str(e)}")
