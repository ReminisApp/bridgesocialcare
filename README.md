# Bridge Social Care

This project requires setting the `OPENAI_API_KEY` environment variable during deployment. Deploy your project quickly and securely with a Vercel pro account (Vercel pro account credentials are provided via email) :

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FReminisApp%2Fbridgesocialcare&env=OPENAI_API_KEY&envDescription=OPENAI%20API%20KEY%20IS%20NEEDED%20FOR%20THIS%20TO%20WORK&envLink=https%3A%2F%2Fplatform.openai.com%2Fapi-keys&project-name=bridgesocialcare&repository-name=bridgesocialcare&redirect-url=https%3A%2F%2Fbridgesocialcare.vercel.app%2F&developer-id=oac_nLNk6tqXGabCqC9Fr6jGO4Dj&production-deploy-hook=Troubleshoot%20PDF%20Deploy&demo-title=Try%20yourself%20at%20bridgesocialcare.vercel.app&demo-description=GPT-4-V%20based%20troubleshooting%20pdfs&demo-url=https%3A%2F%2Fbridgesocialcare.vercel.app&demo-image=https%3A%2F%2Fserver.searchweb.keymate.ai%2F.well-known%2Ficon.png&skippable-integrations=1)

### Post-Deployment Overview

After deploying to a Vercel Pro account (credentials provided via email), you will be redirected to an execution of the built endpoint. This will utilise a 9-page fan manual PDF to extract and return troubleshooting table data.
Basically it will redirect you to [https://[NEWDEPLOYMENT].vercel.app/extract_troubleshoot?publicPdfUrl=https%3A%2F%2Fawss3stack-publickeymatelastda50481a-11bcwu2nql1c1.s3.us-east-1.amazonaws.com%2Fda763fb9-d4b2-4950-b55a-53695917fcc0]([https://aws-s3-image-upload-last-beta.vercel.app/](https://[NEWDEPLOYMENT].vercel.app/extract_troubleshoot?publicPdfUrl=https%3A%2F%2Fawss3stack-publickeymatelastda50481a-11bcwu2nql1c1.s3.us-east-1.amazonaws.com%2Fda763fb9-d4b2-4950-b55a-53695917fcc0))  in the browser



### Assumptions

1. **Troubleshooting Data Extraction**: Only troubleshooting sections with a clear 3-column multi-line table are extracted. These are returned with digital and visible page numbers; each troubleshooting item is assigned a unique ID for database integration. Group IDs are the same between troubleshooting data with the same problem/issue but different things to check and candidate solutions for.
   
2. **Text Filtering**: Non-troubleshooting-related text is filtered out to ensure precision. This filtering is designed around two specific PDFs, indicating potential overfitting. Testing with additional PDFs would be beneficial to evaluate broader applicability.

3. **Environment and Deployment**: Two environments, development and production, are prepared. It's essential that the software functions in production, not just locally. The deployment uses Vercel, a promising PDF library, and Python long-running jobs. Given Vercel's limitations on request entity size (4.5M), the endpoint supports 4.5M inputs via multipart form or an unlimited size through a public PDF URL query parameter.

### Additional Notes

For quick testing of public PDF URLs, use this temporary link to upload a local PDF to get a public URL: [Public PDF URL for Testing](https://aws-s3-image-upload-last-beta.vercel.app/) for PDFs bigger than 4.5M. Note: This service will be discontinued in 3-4 days because it allows anonymous uploads. Example of formatted URL query parameter usage:

- **Encoded**: `https%3A%2F%2Fawss3stack-publickeymatelastda50481a-11bcwu2nql1c1.s3.us-east-1.amazonaws.com%2Fda763fb9-d4b2-4950-b55a-53695917fcc0`
- **Decoded**: `https://awss3stack-publickeymatelastda50481a-11bcwu2nql1c1.s3.us-east-1.amazonaws.com/da763fb9-d4b2-4950-b55a-53695917fcc0`

Depending on the request library, one of them should work. Note: Get parameter query variable approach to get a public pdf URL is entirely wrong; the input should be in the body as a text variable, but this design allowed me to directly send you to the sample deployed page with correct parameters such as https://[NEWDEPLOYMENT].vercel.app/extract_troubleshoot?publicPdfUrl=https%3A%2F%2Fawss3stack-publickeymatelastda50481a-11bcwu2nql1c1.s3.us-east-1.amazonaws.com%2Fda763fb9-d4b2-4950-b55a-53695917fcc0 


For more details on handling large requests in serverless functions on Vercel, see [How to Bypass Vercel's Body Size Limit](https://vercel.com/guides/how-to-bypass-vercel-body-size-limit-serverless-functions). This was the reason I also implemented a public S3 solution.

### OPENAPI.JSON
I created openapi.json. I always keep it updated because, as a fast-growing startup, I learned to use Speakeasy ( Generate SDKs from openapi.json ). It's standard, so it's good to have it. I tried to create modular code.

### Local development 
The local development solution resides at localindex.py. I used pyenv 3.11.3 to run it locally. You can install packages with pip install -r requirements-local.txt and run python localindex.py afterwards it uses 8000 port by default.

### Browser testing 
8. These are the browser testing get parameter test URLs you can try on any browser:
Production: https://bridgesocialcare.vercel.app/extract_troubleshoot?publicPdfUrl=https%3A%2F%2Fawss3stack-publickeymatelastda50481a-11bcwu2nql1c1.s3.us-east-1.amazonaws.com%2F669e1ebd-646e-4053-a138-c0fc02bc87c9  

Development: http://localhost:8000/extract_troubleshoot?publicPdfUrl=https%3A%2F%2Fawss3stack-publickeymatelastda50481a-11bcwu2nql1c1.s3.us-east-1.amazonaws.com%2F669e1ebd-646e-4053-a138-c0fc02bc87c9

This is a sample response from a 9-page fan manual.
```
{
    "result": [
        {
            "page_num": 9,
            "troubleshooting_objects_array": [
                {
                    "conditionOrProblem": "The fan is not operating",
                    "possibleCauseOrThingsToCheck": "The plug is not fully inserted into the wall outlet.",
                    "proposedSolution": "Make sure that the plug is fully inserted into the base AC wall outlet.",
                    "pageNumberShownToHuman": "8",
                    "primaryId": 1,
                    "troubleshootinggroupManualID": 1
                },
                {
                    "conditionOrProblem": "The fan is not operating",
                    "possibleCauseOrThingsToCheck": "The wall outlet experienced an overload.",
                    "proposedSolution": "Unplug the fan. Inspect the main electrical breaker box. If you find a tripped breaker, reset it. If the problem persists, contact a qualified, licensed electrician.",
                    "pageNumberShownToHuman": "8",
                    "primaryId": 2,
                    "troubleshootinggroupManualID": 1
                },
                {
                    "conditionOrProblem": "The fan is not operating",
                    "possibleCauseOrThingsToCheck": "Fuse in plug failed. (For US, Mexico and UK)",
                    "proposedSolution": "Remove and inspect the fuse located in the plug. If the fuse is tripped, replace with the appropriate fuse rated as specified listed on page 2. If the problem persists, contact a qualified, licensed electrician.",
                    "pageNumberShownToHuman": "8",
                    "primaryId": 3,
                    "troubleshootinggroupManualID": 1
                },
                {
                    "conditionOrProblem": "The fan is not operating",
                    "possibleCauseOrThingsToCheck": "The fan is defective.",
                    "proposedSolution": "Contact customer service at service@singfun.com.cn or call 1-866-505-1001 for assistance.",
                    "pageNumberShownToHuman": "8",
                    "primaryId": 4,
                    "troubleshootinggroupManualID": 1
                },
                {
                    "conditionOrProblem": "The remote control does not operate the fan",
                    "possibleCauseOrThingsToCheck": "Incorrect installation.",
                    "proposedSolution": "Inspect the battery to ensure it is correctly installed. Make sure remote is pointed toward front infrared window of fan.",
                    "pageNumberShownToHuman": "8",
                    "primaryId": 5,
                    "troubleshootinggroupManualID": 2
                },
                {
                    "conditionOrProblem": "The remote control does not operate the fan",
                    "possibleCauseOrThingsToCheck": "The battery is expired.",
                    "proposedSolution": "Replace the battery. For best performance we recommend using a DL2032 battery.",
                    "pageNumberShownToHuman": "8",
                    "primaryId": 6,
                    "troubleshootinggroupManualID": 2
                },
                {
                    "conditionOrProblem": "The fan(s) are missing parts",
                    "possibleCauseOrThingsToCheck": "Omitted parts are extremely rare due to stringent quality control during assembly; however there is a possibility that parts can be omitted.",
                    "proposedSolution": "Contact customer service at service@singfun.com.cn or call 1-866-505-1001 for assistance.",
                    "pageNumberShownToHuman": "8",
                    "primaryId": 7,
                    "troubleshootinggroupManualID": 3
                }
            ]
        }
    ]
}
```
This is the other more extended manual provided it takes 2.5 - 3.5 minutes to run them on production Vercel serverless function:
TreadClimber Manual 
https://bridgesocialcare.vercel.app/extract_troubleshoot?publicPdfUrl=https%3A%2F%2Fawss3stack-publickeymatelastda50481a-11bcwu2nql1c1.s3.us-east-1.amazonaws.com%2Fda763fb9-d4b2-4950-b55a-53695917fcc0 

I didn't increase the timeout setting of the local sanic server because it's only for development purposes.
http://localhost:8000/extract_troubleshoot?publicPdfUrl=https%3A%2F%2Fawss3stack-publickeymatelastda50481a-11bcwu2nql1c1.s3.us-east-1.amazonaws.com%2Fda763fb9-d4b2-4950-b55a-53695917fcc0




Considerations and learnings:
1. Every execution gives a different function-calling result because the vision model doesn't guarantee that it will run the same thing with the same parameters. The workaround I tried was using another LLM call that allows the 'seed' parameter to make function calling more consistent. However, the 'seed' parameter didn't give system_fingerprint properly on the newest model, and I had to revert that because it didn't work as explained in the OpenAI docs. I solved apparent issues with prompt engineering.
2. I tried to separate the concerns while creating Python packages.
3. I started test automation in the tests folder, but they're taking too long to run, significantly when I change prompts, which affects the whole PDF. It will only be needed when a more significant change is made.
4. I went after the S3 PDF path because my customers at Keymate.AI were uploading PDFs, and we were already splitting and only reading texts (without OCR or vision ). Understanding text from images and explaining tables were requirements, but they were down on the to-do list. I went after a production use case for this project and prepared an excellent solution. I am excited to see it in the wild while others use it!

Feel free to comment or reach out to me at ozgur@keymate.ai
