#For Vercel it's mandatory to keep this in api folder
from sanic import Sanic
from sanic.response import redirect, text, json as sanic_json
import json
import os
import openai
import requests
import tempfile
from urllib.parse import urlparse
import utils
from services.troubleshooting_service import extract_troubleshoot_pdf, assign_ids_to_conditions
app = Sanic()

@app.route("/", methods=["GET", "OPTIONS", 'HEAD'])
async def healthcheck(request):
    redirect_url = request.args.get("deployment-url", "")
    if redirect_url == "":
        return sanic_json({"status": "healthy", "instruction": "Use 'file' multipart form key to send a local file, it should be lower than 4.5M alternatively you can use a public pdf url (i.e. presigned s3 URL )"})
    else:
        return redirect(redirect_url+"/extract_troubleshoot?publicPdfUrl=https%3A%2F%2Fawss3stack-publickeymatelastda50481a-11bcwu2nql1c1.s3.us-east-1.amazonaws.com%2F669e1ebd-646e-4053-a138-c0fc02bc87c9")



@app.route("/extract_troubleshoot", methods=['GET',"OPTIONS", 'HEAD'])
async def extract_troubleshoot(request):
    file = request.files.get('file')

    if file:
        # Process or save the file here
        file_body = file.body
        file_name = file.name


        # Construct the full path where the PDF will be saved
        full_path = os.path.join("/tmp", file_name)
        try:
            with open(full_path, 'wb') as f:
                f.write(file_body)
        except Exception as e:
            return sanic_json({"message": f"An error occurred: {e}"}, status=500)
    elif request.args.get('publicPdfUrl'):
        pdfUrl = request.args.get('publicPdfUrl')
        response = requests.get(pdfUrl, allow_redirects=True)

        # Parse the URL to extract the file name
        parsed_url = urlparse(pdfUrl)
        file_name = os.path.basename(parsed_url.path)

        # Construct the full path where the PDF will be saved
        full_path = os.path.join("/tmp", file_name)

        if response.status_code == 200:
            with open(full_path, 'wb') as f:
                f.write(response.content)
        else:
            return sanic_json({"message": "Error while downloading the file"}, status=400)
    else:
        return sanic_json({"message": "File input has not been provided. Use 'file' multipart form key to send a local file, it should be lower than 4.5M alternatively you can use a public pdf url (i.e. presigned s3 URL )"}, status=400)

    troubleshooting_section = extract_troubleshoot_pdf(full_path)
    os.remove(full_path)
    troubleshooting_section_with_ids = assign_ids_to_conditions(troubleshooting_section)

    return sanic_json({"result": troubleshooting_section_with_ids})

