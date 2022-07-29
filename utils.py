import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
load_dotenv()
import os
import requests
from requests.structures import CaseInsensitiveDict

def sentEmail(subject,body,To,CCed,BCCed):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(os.getenv('GMAIL_USER'), os.getenv('GMAIL_KEY'))
            try:
                msg = EmailMessage()
                msg.set_content('')
                msg.add_alternative(body, subtype='html')
                msg['Subject'] = subject
                msg['From'] = 'autolopjira@gmail.com'
                msg['To'] = ', '.join(To)
                msg['Cc'] = ', '.join(CCed)
                msg['Bcc'] = ', '.join(BCCed)
                smtp.send_message(msg)
            except:
                print("Something went wrong!!!")
    print("DONE!")


def random_joke_image():
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    # x = requests.get('https://icanhazdadjoke.com',headers=headers)
    # joke=x.json()['joke']
    
    x = requests.get('https://api.chucknorris.io/jokes/random?category=dev',headers=headers)
    joke=x.json()['value']
    if str(x.status_code)=='200':
        return f"<h5>{joke}</h5>"
    else:
        return''

def jira2htmltable(jira_json):
    count_empties=0
    sum=0
    for i in jira_json:
        if i['remaining_estimate']=='':
            count_empties+=1
        else:
            periods=i['remaining_estimate'].split(' ')
            for period in periods:
                if 'w' in period:
                    sum+=int(period.replace('w',''))*5*8*60
                elif 'd' in period:
                    sum+=int(period.replace('d',''))*8*60
                elif 'h' in period:
                    sum+=int(period.replace('h',''))*60
                elif 'm' in period:
                    sum+=int(period.replace('m',''))
    
    
    jira_tickets_table="""    <table style="width:100%">
    <thead>
        <tr><th>Key</th><th>Issue Type</th><th>Sprint</th><th>Title</th><th>Remaining Estimate</th><th>Status</th><th>High Priority</th></tr>
    </thead>
    <tbody>
    """
    sumH1=0
    for issue in jira_json:
        jira_tickets_table +='<tr><td style="width:9%"><a href="https://jsw.ibm.com/browse/{}">{}</a></td><td style="width:9%">{}</td><td style="width:15%">{}</td><td style="width:50%">{}</td><td style="width:8%">{}</td><td style="width:5%">{}</td><td style="width:5%">{}</td></tr>'.format(issue['key'],issue['key'],issue['type'],issue['sprint'],issue['title'],issue['remaining_estimate'],issue['status'],'✔️' if issue['highPriority'] else '')
        if issue['highPriority']==True:
            sumH1+=1
    jira_tickets_table +="""
    </tbody>
    </table>"""
    summary='Remaining backlog <b>{:0.2f} days</b> including <b>{}</b> defects with no estimation. High Priority Remaining <b>{}</b>'.format(sum/60/8,count_empties,sumH1)
    jira_tickets_table+=summary

    return jira_tickets_table

def footer():
    f=''
    f += """<h1>LET'S GO!</h1>
    <h4>PS1: Random Chuck Norris Joke (Share it with the team, if it is worth it 🤷)</h4>"""
    f += random_joke_image()
    f +="""<br>
    <h4>PS2: <a href='https://www.youtube.com/watch?v=ltcHzgUc944&ab_channel=UEFAChampionsLeagueNews'>Click here on your own responsibility</a></h4>
    <h3>This is an automated email created by <b>LEPA-BOT</b>. Please do not reply. 🙏</h3>"""

    return f

def header():
    return """<!DOCTYPE html>
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
        }
        th {
        background-color: #96D4D4;
        }
        th, td {
        padding: 5px;
        }
    </style>
    </head>"""