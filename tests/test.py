import unittest
import requests



class MyTestCase(unittest.TestCase):
    def test_treadclimber_manual(self):
        url = "https://bridgesocialcare.vercel.app/extract_troubleshoot?publicPdfUrl=https%3A%2F%2Fawss3stack-publickeymatelastda50481a-11bcwu2nql1c1.s3.us-east-1.amazonaws.com%2Fda763fb9-d4b2-4950-b55a-53695917fcc0"
        response = requests.get(url)
        assert response.status_code == 200
        # Additional assertions can be added to verify the response content
        assert 'result' in response.json()



if __name__ == '__main__':
    unittest.main()
