import requests
from datetime import datetime, timedelta
import re
from pikepdf import Pdf
import io
import argparse

def get_arcinfo_pdf(date: datetime, output_file: str, username: str, password: str) -> "Pdf":
    """Creates and save a pdf of the ArcInfo edition for the specified date

    Args:
        date (datetime): the edition date
        output_file (str): path of the output file
        username (str): username to use to login
        password (str): password to use to login
    """

    output = Pdf.new()

    # Use a session to store the authentication cookie
    with requests.Session() as s:

        # Override requests user agent which is denied access
        s.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
            }
        )

        # Login
        params = {"_username": username, "_password": password}
        r = s.post("https://jd.arcinfo.ch/arcinfo/login/", data=params)
        if "arcinfo_access_token" not in s.cookies:
            print("Login error")

        # Get current edition page
        # url format: "https://jd.arcinfo.ch/arcinfo/2021-12-24/view"
        url = "https://jd.arcinfo.ch/arcinfo/{0}/view".format(date.strftime("%Y-%m-%d"))
        r = s.get(url)

        # Find all pages pdf of current edition
        pdfs = re.findall("\/editions\/arcinfo\/.{12}\/pdf\/page\d+.pdf", r.text)

        if len(pdfs) > 0:
            # Download them and append to output file
            base_url = "https://jd.arcinfo.ch"
            for pdf in pdfs:
                url = base_url + pdf
                r = s.get(url)
                if r.ok:
                    f = io.BytesIO(r.content)
                    src = Pdf.open(f)
                    output.pages.extend(src.pages)

        else:
            print("Edition does not exists")

    if len(output.pages) > 0:
        output.save(output_file)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Get arcinfo pdf of the date')

    parser.add_argument("username", help="ArcInfo username")
    parser.add_argument("password", help="ArcInfo password")
    parser.add_argument("output_folder", help="Output folder")

    args = parser.parse_args()

    date = datetime.now()
    get_arcinfo_pdf(date, "{0}/{1}.pdf".format(args.output_folder, date.strftime("%Y-%m-%d")), args.username, args.password)