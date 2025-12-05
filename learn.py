import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Define the API endpoints for PostgreSQL and MongoDB environments
postgres_endpoints = {
    "Staging": "https://ingress-rdei-ashburn-cct-01.monitoring.comcast.net/alerta-54c17572-8414-4865-b4cc-39debad61a38/api/alerts?q=status:(open)&environment=Staging",
    "QA": "https://ingress-rdei-ashburn-cct-01.monitoring.comcast.net/alerta-54c17572-8414-4865-b4cc-39debad61a38/api/alerts?q=status:(open)&environment=Qa",
    "Dev": "https://ingress-rdei-ashburn-cct-01.monitoring.comcast.net/alerta-54c17572-8414-4865-b4cc-39debad61a38/api/alerts?q=status:(open)&environment=Development",
    "Prod": "https://ingress-rdei-ashburn-cct-01.monitoring.comcast.net/alerta-54c17572-8414-4865-b4cc-39debad61a38/api/alerts?q=status:(open)&environment=Production"
}
mongo_endpoints = {
    "Staging": "https://ingress-rdei-ashburn-cct-01.monitoring.comcast.net/alerta-30ac2b4b-2554-46b2-b2f7-5b703acf824d/api/alerts?q=status:(open)&environment=Staging",
    "QA": "https://ingress-rdei-ashburn-cct-01.monitoring.comcast.net/alerta-30ac2b4b-2554-46b2-b2f7-5b703acf824d/api/alerts?q=status:(open)&environment=Qa",
    "Dev": "https://ingress-rdei-ashburn-cct-01.monitoring.comcast.net/alerta-30ac2b4b-2554-46b2-b2f7-5b703acf824d/api/alerts?q=status:(open)&environment=Development",
    "Prod": "https://ingress-rdei-ashburn-cct-01.monitoring.comcast.net/alerta-30ac2b4b-2554-46b2-b2f7-5b703acf824d/api/alerts?q=status:(open)&environment=Production"
}

# Define the headers for PostgreSQL and MongoDB
postgres_headers = {
    "x-api-key": "l8MuMWW33A2WQbHSEB-CGubJskF_-abSTKtFRvJt"
}
mongo_headers = {
    "x-api-key": "2AtGIFHdO2_nIXRybS0GTkWbk1K0nwby4BUeSaMQ"
}

# Initialize counters for the total number of open incidents
total_postgres_non_prod_open_incidents = 0
total_postgres_prod_open_incidents = 0
total_mongo_non_prod_open_incidents = 0
total_mongo_prod_open_incidents = 0

# Function to get open incidents count
def get_open_incidents(endpoints, headers):
    total_non_prod_open_incidents = 0
    total_prod_open_incidents = 0
    for environment, url in endpoints.items():
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict) and 'statusCounts' in data:
                open_count = data['statusCounts'].get('open', 0)
                if environment == "Prod":
                    total_prod_open_incidents += open_count
                else:
                    total_non_prod_open_incidents += open_count
            else:
                print(f"Unexpected response format for {environment}: {data}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve data for {environment}: {e}")
    return total_non_prod_open_incidents, total_prod_open_incidents

# Get open incidents for PostgreSQL and MongoDB
total_postgres_non_prod_open_incidents, total_postgres_prod_open_incidents = get_open_incidents(postgres_endpoints, postgres_headers)
total_mongo_non_prod_open_incidents, total_mongo_prod_open_incidents = get_open_incidents(mongo_endpoints, mongo_headers)

# Create the HTML email content with tables for PostgreSQL and MongoDB
html_content = f"""
<html>
<head></head>
<body>
<center>
    <h2 style="color:blue;">Open Incident Report</h2>
    <h3>PostgreSQL</h3>
    <table border="1">
        <tr>
            <th>Environment</th>
            <th>Open Incidents</th>
        </tr>
        <tr>
            <td style="text-align: center;">Nonprod</td>
            <td style="text-align: center;color:red;">{total_postgres_non_prod_open_incidents}</td>
        </tr>
        <tr>
            <td style="text-align: center;">Prod</td>
            <td style="text-align: center;color:red;">{total_postgres_prod_open_incidents}</td>
        </tr>
    </table>
    <h3>MongoDB</h3>
    <table border="1">
        <tr>
            <th>Environment</th>
            <th>Open Incidents</th>
        </tr>
        <tr>
            <td style="text-align: center;">Nonprod</td>
            <td style="text-align: center;color:red;">{total_mongo_non_prod_open_incidents}</td>
        </tr>
        <tr>
            <td style="text-align: center;">Prod</td>
            <td style="text-align: center;color:red;">{total_mongo_prod_open_incidents}</td>
        </tr>
    </table>
</center>
</body>
</html>
"""

# Set up the email parameters
sender_email = "devxpgnotifications@comcast.com"
receiver_email = "Vignesh_Rajaram@comcast.com"
#cc_email = "kishore_v.b.mukkamala@comcast.com,Gowtham_Elangovan@comcast.com"
subject = "Incident Report"

# Create the email message
msg = MIMEMultipart("alternative")
msg["Subject"] = subject
msg["From"] = sender_email
msg["To"] = receiver_email
#msg["Cc"] = cc_email

# Attach the HTML content to the email
part = MIMEText(html_content, "html")
msg.attach(part)

# Send the email using the local SMTP server
with smtplib.SMTP('mailrelay.comcast.com', 25) as server:
    server.sendmail(sender_email, receiver_email, msg.as_string())

print("Email sent successfully!")
