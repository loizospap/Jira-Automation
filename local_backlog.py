from email.mime.text import MIMEText
from jira import JIRA
from utils import sentEmail, random_joke_image, jira2htmltable, footer, header
from dotenv import load_dotenv

load_dotenv()
import os
from datetime import datetime

mocked=True
# Query

sprints=["Package 6.0.X","Package 6.X","High Priority","Package 6+", "Sprint XX (Ready for Dev)"]

# sprints=["Package 6.0.5"]
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

# Email participants
CCed=['Loizos.Papachristoforou1@ibm.com']
BCCed = []
summaryTo=['Panayiotis.Petrides1@ibm.com','elena.panagiotou@cy.ibm.com']
# ,'a.papageorgiou@cy.ibm.com']
summaryCCed=['Loizos.Papachristoforou1@ibm.com']
if mocked : summaryTo=summaryCCed
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

sum_H1=0
for index,developer in enumerate(developers):
    print('Search Query')
    print('=============================')
    # search_query.append('project in ("Hellenic Bank LOP PROD", "Hellenic Bank - LOP") AND status in ('+','.join(f'"{w}"' for w in statuses)+') AND Sprint in ('+','.join(f'"{w}"' for w in sprints)+') AND assignee in ("'+developer['email']+'")')
    search_query.append('project in ("Hellenic Bank LOP PROD", "Hellenic Bank - LOP") AND status in ('+','.join(f'"{w}"' for w in statuses)+') AND (Sprint = "Package" or Sprint = 113523) AND assignee in ("'+developer['email']+'")')
    
    print(search_query[-1])
    print('=============================')
    
    issues_in_proj = jira.search_issues(search_query[-1],maxResults=400)

    print(f'Tickets: ', len(issues_in_proj))

    email_issues=[]
    for issue in issues_in_proj:
        sprint=''
        if len(issue.raw['fields']['customfield_10104'])>0:
            # for index,sp in enumerate(issue.raw['fields']['customfield_10104']):
            sprint=issue.raw['fields']['customfield_10104'][-1].split(',')[3].split('=')[1]
        
        # print('{} | {}| {} | {}'.format(issue.fields.issuetype.name.ljust(20),issue.key.ljust(15), sprint.ljust(20), issue.fields.summary))

        remainingEstimate='' if 'remainingEstimate' not in issue.raw['fields']['timetracking'] else issue.raw['fields']['timetracking']['remainingEstimate']

        email_issues.append(
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

    email_issues.sort(key=lambda x:x.get('sprint'))
    inP6=list(filter(lambda x: 'Package 6' in x.get('sprint'), email_issues)) 
    notP6=list(filter(lambda x: 'Package 6' not in x.get('sprint'), email_issues)) 
    notP6.sort(key=lambda x:x.get('highPriority'),reverse=True)
    email_issues=inP6+notP6

    for issue in email_issues[:10]:
        print('{} | {}| {} | {} | {} | {} |'.format(issue['key'].ljust(20),issue['type'].ljust(20),issue['sprint'].ljust(20),issue['title'][:20].ljust(20),issue['remaining_estimate'].ljust(20),issue['status'],'✔️' if issue['highPriority'] else ''))
        sum_H1+=1 if issue['highPriority'] else 0

    jira_html_tables.append(jira2htmltable(email_issues))
    
    subject=f'LOP🎯 {datetime.now().strftime("%d/%m/%Y %H:%M")} - DAILY BACKLOG UPDATE 💪 '

    html=''
    html +=header() 

    html +="""<body>
    <p>Hello Team 🚀🚀🚀, <br><br>Below you can find your backlog. Kindly consider the followings:</p>
    <p>(1) The <b>priority</b> is as follows : """+' 👉 '.join(sprints)+"""([1] 'HBPROD' [2] 'HBLOP')  👉 🏆</p> 
    <p>(2) When starting to work on a defect not in Sprint, please make sure that there will be no impact on Sprint deliverables</p>
    <p>(3) If [Remaining Estimate] on reopen is empty, please add estimation for your fix.</p>
    <p><b>Search Query</b> : """+search_query[-1]+"""</p>
    <br>"""

    html +=jira_html_tables[-1]
    
    html +=footer()

    if (mocked==False):
        if 'Marianna' in developer['email']:
            To=['mekenoglu@acgoldman.com','mvahabi@acgoldman.com']
        else:
            tempTo=[developer]
            To=[]
            for t in tempTo:
                To.append(t['email'])

        print(f"To: {', '.join(To)}")
        print(f"CC: {', '.join(CCed)}")
        print(f"BCC: {', '.join(BCCed)}")
        print(f"Do you want to send an email: ")
        if developer['sentEmailFlag']:
            sentEmail(subject,body=html,To=To,CCed=CCed,BCCed=BCCed)
    else:
        To=['Loizos.Papachristoforou1@ibm.com']
        CCed=[]
        BCCed = []
        print(f"To: {', '.join(To)}")
        print(f"CC: {', '.join(CCed)}")
        print(f"BCC: {', '.join(BCCed)}")
        print(f"Do you want to send an email: ")
        if developer['sentEmailFlag']:
            sentEmail(subject,body=html,To=To,CCed=CCed,BCCed=BCCed)


# Summary
subject=f'LOP🎯 {datetime.now().strftime("%d/%m/%Y %H:%M")} - LOCAL TEAM BACKLOG UPDATE 💪 '

html=''
html+=header() 
html+="""<body>
<p>Hello Team 🚀🚀🚀, <br><br>Below you can find your local team's backlog. Kindly consider the followings:</p>
<p>(1) The <b>priority</b> is as follows : """+' 👉 '.join(sprints)+""" 👉 🏆</p> 
<p>(2) When starting to work on a defect not in Sprint, please make sure that there will be no impact on Sprint deliverables</p>
<p>(3) If [Remaining Estimate] on reopen is empty, please add estimation for your fix.</p>

<p style="font-size:20px; font-weight: bold;">High Priority Counter (on Dev)  <span style="font-size:20px; font-weight: bold;color:red">"""+str(sum_H1)+"""</span></p>
"""
html+='<br><hr style="height:2px;border-width:0;color:gray;background-color:gray"><hr style="height:2px;border-width:0;color:gray;background-color:gray">'
for index,developer in enumerate(developers):
    html+="""<p><b>Email</b> : """+developer['email']+"""</p>"""
    html+="""<p><b>Search Query</b> : """+search_query[index]+"""</p>"""
    html+=jira_html_tables[index]
    html+='<br><hr style="height:2px;border-width:0;color:gray;background-color:gray"><hr style="height:2px;border-width:0;color:gray;background-color:gray">'

html+=footer()
html+="""
</body>
</html>
"""

if (mocked==False):
    sentEmail(subject,body=html,To=summaryTo,CCed=summaryCCed,BCCed=summaryBCCed)
else:
    summaryTo=['Loizos.Papachristoforou1@ibm.com']
    summaryCCed=['Loizos.Papachristoforou1@ibm.com']
    summaryBCCed=[]
    sentEmail(subject,body=html,To=summaryTo,CCed=summaryCCed,BCCed=summaryBCCed)