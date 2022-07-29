from jira import JIRA
from tkinter import *

def sortVersions(version):
    version = str(version[6:]).split(".")
    return [int(x) for x in version]

tokenfile = open("APItoken.txt")
API_TOKEN = tokenfile.read()
tokenfile.close()

jira = JIRA(server="https://jsw.ibm.com", token_auth=(API_TOKEN))
query = "project in (HBLOP,HBPROD) AND status = Ready AND fixVersion = {} AND assignee in (\"{}\")"
versions = [version.name for version in jira.project_versions("HBLOP") if version.name.startswith("HBLOP")]
versions.sort(reverse=True, key=sortVersions)
versions = versions[:9]
assignees = set()

window = Tk()
window.title("Set Testing")
window.geometry( "500x500" )

fixVersionSelection = Frame(window)
Label(fixVersionSelection, text="Select Fix Version:").grid(row=0, column=0)
versionMenu = StringVar(window, value=versions[0])
drop = OptionMenu(fixVersionSelection, versionMenu, *versions)
drop.grid(row=0, column=1)
fixVersionSelection.pack(pady=30)

options = Frame(window)

devBoxes = Frame(options)
Label(devBoxes, text="Select Developers:").pack(pady=10, anchor=W)
devfile = open("developers.txt")
devBoxVals = {}

for line in devfile:
    dev = line.strip()
    if dev:
        devBoxVals[dev] = IntVar()
        check = Checkbutton(devBoxes, text=dev, variable=devBoxVals[dev])
        check.pack(anchor=W)

devBoxes.grid(row=0, column=0, sticky=NW, padx=10)

testerButtons = Frame(options)
Label(testerButtons, text="Select Tester:").pack(pady=10, anchor=W)
testerfile = open("testers.txt")
testerVal = StringVar(window, " ")

for line in testerfile:
    tester = line.strip()
    if tester:
        button = Radiobutton(testerButtons, text=tester, variable=testerVal, value=tester)
        button.pack(anchor=W)

testerButtons.grid(row=0, column=1, sticky=NW, padx=10)

options.pack(pady=20)

devfile.close()

def setTesting():
    try:
        fixVersion = versionMenu.get()
        issueCount = 0
        updatedIssues = set()
        tester = testerVal.get()

        for dev in devBoxVals:
            if devBoxVals[dev].get():
                assignees.add(dev)
            elif dev in assignees:
                assignees.remove(dev)

        for issue in jira.search_issues(query.format(fixVersion, '\",\"'.join(assignees)), maxResults=1000):
            jira.assign_issue(issue.key, tester)
            jira.transition_issue(issue.key, "Testing")
            issueCount += 1
            updatedIssues.add(issue.key)
        
        popup = Toplevel()
        popup.title("Set Testing Complete")
        popup.geometry("500x200")
        successMsg = "Set Testing Completed Succesfully.\n {} issues were reassigned to {} and status set to Testing.\n The updated issues are: {}"
        Label(popup, text=successMsg.format(issueCount, tester, ', '.join(updatedIssues))).pack(pady=20)
        buttons = Frame(popup)
        Button(buttons, text="OK", command=popup.destroy).grid(row=0, column=0, padx=30)
        Button(buttons, text="Close", command=window.destroy).grid(row=0, column=1, padx=30)
        buttons.pack(pady=30)
    except Exception as e:
        popup = Toplevel()
        popup.title("Set Testing Failed")
        popup.geometry("500x200")
        Label(popup, text="Set Testing Failed.\n {}".format(e)).pack(pady=20)
        Button(popup, text="Exit", command=window.destroy).pack(pady=30)

button = Button( window , text = "Set Testing" , command = setTesting )
button.pack(pady=20)

window.mainloop()
