from flask import Flask, render_template,request,redirect, url_for, flash, jsonify
from email.mime.text import MIMEText
from jira import JIRA
from utils import sentEmail, random_joke_image, jira2htmltable, footer, header
from dotenv import load_dotenv
import os
import requests

app = Flask(__name__)

# Email participants
CCed=['Loizos.Papachristoforou1@ibm.com']
BCCed = []
summaryTo=['Panayiotis.Petrides1@ibm.com','elena.panagiotou@cy.ibm.com']
# ,'a.papageorgiou@cy.ibm.com']
summaryCCed=['Loizos.Papachristoforou1@ibm.com']
# if mocked : summaryTo=summaryCCed
summaryBCCed=[]

print(summaryTo)

user = os.getenv('JIRA_USER')
apikey = os.getenv('JIRA_KEY')
server = os.getenv('JIRA_URL')

options = {
 'server': server
}

jira = JIRA(options, basic_auth=(user,apikey) )

summary=[]
search_query=[]
jira_html_tables=[]
developers=[
    {'email':"Marianna.Piripitsi@cy.ibm.com",'sentEmailFlag':False},
    {'email':"FILIPPOS.HADJITHEODOULOU@ibm.com",'sentEmailFlag':False},
    {'email':"Ioannis.Yiangou@ibm.com",'sentEmailFlag':False},
    {'email':"Loizos.Papachristoforou1@ibm.com",'sentEmailFlag':False},
    {'email':"mohamedashraf@eg.ibm.com",'sentEmailFlag':False},
    {'email':"rowan.ibrahim@ibm.com",'sentEmailFlag':False},
    {'email':"hossam.ahmed@ibm.com",'sentEmailFlag':False},
    {'email':"abdelrahman.mahmoud@ibm.com",'sentEmailFlag':False},
    {'email':"alihamada@eg.ibm.com",'sentEmailFlag':False},
    {'email':"sameh.mohamed@ibm.com",'sentEmailFlag':False},
    {'email':"Aly.Hesham@ibm.com",'sentEmailFlag':False},
    {'email':"islam.hefnawy@eg.ibm.com",'sentEmailFlag':False},
    {'email':'abdel-moniem.el-tantawi@ibm.com','sentEmailFlag':False}
]

statuses=["To Do", "Awaiting Feedback", "Blocked", "In Progress", "Reviewing"]

initialiseObject={
    'devs':developers,
    'status':statuses,
    'selected_devs':[],
    'email_issues':[],
    'search_query':[]
}

email_issues=[]
@app.route('/')
def init():
   return render_template('index.html',initialiseObject=initialiseObject)


@app.route("/backlog/", methods=['GET', 'POST'])
def move_forward():
    #Moving forward code
    forward_message = "Moving Forward..."
    initialiseObject["search_query"]=[]

    initialiseObject["selected_devs"]=[]
    if request.method == 'POST':
        initialiseObject["selected_devs"] = request.form.getlist('myform')

    initialiseObject["email_issues"]=[]

    if len(initialiseObject["selected_devs"])==0:
        return redirect(url_for('init'))

    for index,developer in enumerate(initialiseObject["selected_devs"]):
        print('Search Query')
        print('=============================')
        # search_query.append('project in ("Hellenic Bank LOP PROD", "Hellenic Bank - LOP") AND status in ('+','.join(f'"{w}"' for w in statuses)+') AND Sprint in ('+','.join(f'"{w}"' for w in sprints)+') AND assignee in ("'+developer['email']+'")')
        initialiseObject["search_query"].append('project in ("Hellenic Bank LOP PROD", "Hellenic Bank - LOP") AND status in ('+','.join(f'"{w}"' for w in statuses)+') AND (Sprint = "Package" or Sprint = 113523) AND assignee in ("'+developer+'")')
        
        print( initialiseObject["search_query"][-1])
        print('=============================')
        
        issues_in_proj = jira.search_issues( initialiseObject["search_query"][-1],maxResults=400)

        print(f'Tickets: ', len(issues_in_proj))

        initialiseObject["email_issues"].append([])
        for issue in issues_in_proj:
            sprint=''
            if len(issue.raw['fields']['customfield_10104'])>0:
                sprint=issue.raw['fields']['customfield_10104'][-1].split(',')[3].split('=')[1]
            
            remainingEstimate='' if 'remainingEstimate' not in issue.raw['fields']['timetracking'] else issue.raw['fields']['timetracking']['remainingEstimate']

            initialiseObject["email_issues"][index].append(
                {
                    'type':issue.fields.issuetype.name,
                    'key':issue.key,
                    'sprint':sprint,
                    'title':issue.fields.summary,
                    'remaining_estimate': remainingEstimate,
                    'status':issue.fields.status,
                    'highPriority':'H1' in issue.raw['fields']['labels'] 
                }
            )
            
        initialiseObject["email_issues"][index].sort(key=lambda x:x.get('sprint'))
        inP6=list(filter(lambda x: 'Package 6' in x.get('sprint'),  initialiseObject["email_issues"][index])) 
        notP6=list(filter(lambda x: 'Package 6' not in x.get('sprint'),  initialiseObject["email_issues"][index])) 
        notP6.sort(key=lambda x:x.get('highPriority'),reverse=True)
        initialiseObject["email_issues"][index]=inP6+notP6

        for issue in  initialiseObject["email_issues"][index][:10]:
            print('{} | {}| {} | {} | {} | {} |'.format(issue['key'].ljust(20),issue['type'].ljust(20),issue['sprint'].ljust(20),issue['title'][:20].ljust(20),issue['remaining_estimate'].ljust(20),issue['status'],'✔️' if issue['highPriority'] else ''))

        print('=============================')

    return render_template('index.html', initialiseObject=initialiseObject)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))