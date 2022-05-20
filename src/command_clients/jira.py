import requests
from requests.auth import HTTPBasicAuth
import json
from .jiradatabase import jiradatabase
from datetime import datetime

from lib.utils import COLOR_RED, COLOR_GREEN, COLOR_BLUE


MISSING_DOMAIN_ERROR = {
    "title": "ERROR",
    "description": "Missing Domain!",
    "color": COLOR_RED
}
MISSING_CONNECTION_ERROR = {
    "title": "ERROR",
    "description":"The user has to connect first",
    "color": COLOR_RED
}

class JiraClient():
    def __init__(self) -> None:
        self.db = jiradatabase()
        self.users = []

    def connect_user(self, login_data):
        self.db = jiradatabase()
        dc_userid = login_data["dc_user"].id
        email = login_data["email"]
        jiratoken = login_data["jiratoken"]
        jiraid = login_data["account_id"]
        return self.db.connect_user(dc_userid, email, jiratoken, jiraid)

    def setup_domain(self, domain):
        self.db = jiradatabase()
        return self.db.init_domain(domain)

    def get_issues_by_user(self, user):
        if isinstance(user, dict):
            if not self.user_exist(user["id"]):
                return MISSING_CONNECTION_ERROR
            j_user = self.get_jirauser_by_dcuserID(user["id"])
        else:
            if not self.user_exist(user.id):
                return MISSING_CONNECTION_ERROR
            j_user = self.get_jirauser_by_dcuserID(user.id)
        if j_user != None:
            return j_user.get_issues_by_user()
        else:
            return MISSING_DOMAIN_ERROR

    def get_issue_details(self, user, issuename):
        if not self.user_exist(user.id):
            return MISSING_CONNECTION_ERROR
        j_user = self.get_jirauser_by_dcuserID(user.id)
        if j_user != None:
            return j_user.get_issue_details(issuename)
        else:
            return MISSING_DOMAIN_ERROR

    def get_all_projects(self, user):
        if not self.user_exist(user.id):
            return MISSING_CONNECTION_ERROR
        j_user = self.get_jirauser_by_dcuserID(user.id)
        if j_user != None:
            return j_user.get_all_project()
        else:
            return MISSING_DOMAIN_ERROR

    def get_projects_by_user(self, user):
        if isinstance(user, dict):
            if not self.user_exist(user["id"]):
                return MISSING_CONNECTION_ERROR
            j_user = self.get_jirauser_by_dcuserID(user["id"])
        else:
            if not self.user_exist(user.id):
                return MISSING_CONNECTION_ERROR
            j_user = self.get_jirauser_by_dcuserID(user.id)
        if j_user != None:
            return j_user.get_projects_by_user()
        else:
            return MISSING_DOMAIN_ERROR

    def comment_on(self, user, key, comment):
        if not self.user_exist(user.id):
            return MISSING_CONNECTION_ERROR
        j_user = self.get_jirauser_by_dcuserID(user.id)
        return j_user.api_comment_on(key, comment)



    def get_jirauser_by_dcuserID(self, dcuserID):
        if self.db.get_domain() != None:
            user = JiraUser(self.db.get_user_email(dcuserID), self.db.get_user_jiratoken(dcuserID), dcuserID, self.db.get_domain())
            return user
        else:
            return None

    def user_exist(self, dcuserID):
        self.db = jiradatabase()
        if self.db.user_exist(dcuserID):
            return True
        else:
            return False


class JiraUser():
    def __init__(self, email, token, dcuserID, domain):
        self.email = email
        self.jiratoken = token
        self.userid = dcuserID
        self.domain = domain
        self.auth = HTTPBasicAuth(email, self.jiratoken)

    #API-Anfrage - übergibt alle Issue-Keynamen in einem Projekt
    def __api_get_all_issues_by_project(self, project: str):

        url = "https://" + self.domain + ".atlassian.net/rest/api/3/search"

        headers = {
            "Accept": "application/json"
        }

        query = {
            "jql": "project =" + project
        }

        response = requests.request(
            "GET",
            url,
            headers=headers,
            params=query,
            auth=self.auth
        )

        if response.status_code == 200:
            data = response.json()
            issues = data["issues"]
            return issues, None

        elif response.status_code == 400:
            return None, "JQL query is invalid; Code Error"

        elif response.status_code == 401:
            return None, "authentication credentials are incorrect or missing"
        
        else:
            return None, "UKNOWN ERROR"

    #API-Anfrage - übergibt alle existierenden Projekte in der Domain als JSON
    def __api_get_all_projects(self):
        url = "https://" + self.domain + ".atlassian.net/rest/api/3/project"

        headers = {
            "Accept": "application/json"
        }

        response = requests.request(
            "GET",
            url,
            headers=headers,
            auth=self.auth
        )

        if response.status_code == 200:
            projects = response.json()
            return projects, None

        elif response.status_code == 401:
            return None, "authentication credentials are incorrect or missing"

        else:
            return None, "UNKNOWN Error"

    #API-Anfrage - übergibt das Issue über dem Keynamen des Issue
    def __api_get_issue_by_key(self, key):
        url = "https://" + self.domain + ".atlassian.net/rest/api/3/issue/" + key

        headers = {
            "Accept": "application/json"
        }

        response = requests.request(
            "GET",
            url,
            headers=headers,
            auth=self.auth
        )

        if response.status_code == 200:
            issue = response.json()
            return issue, None

        elif response.status_code == 401:
            return None, "authentication credentials are incorrect or missing"

        elif response.status_code == 404:
            return None, "issue is not found or the user does not have permission to view it"

        else:
            return None, "error"

    #übergibt alle Projektnamen in einer Liste - veraltet      
    def __get_all_project_names(self):
        projects, error = self.__api_get_all_projects()
        list = []
        if projects is not None:
            for project in projects:
                list.append(project["key"])
            return list, None
        else:
            return None, error

    #übergibt alle Projektnamen als Dictionary für ein Embed
    def get_all_project(self):
        projects, error = self.__api_get_all_projects()
        if projects is not None:
            list = []
            count = 0
            for project in projects:
                list.append(project["key"] + ": " + project["name"])
                count += 1

            delimiter = " ,"
            projectnames = delimiter.join(list)

            fields = {
                "Issues": projectnames
            }
            embedstructure = {
                    "title": "Projects",
                    "description": None,
                    "fields": fields,
                    "color": COLOR_BLUE
                }
        else:
            embedstructure = {
                    "title": "ERROR",
                    "description": f"{error} or no project exists",
                    "color": COLOR_RED
                }

        return embedstructure

    #übergibt alle Projekte, bei den ein User eine Aufgabe hat als Dictionary für ein Embed
    def get_projects_by_user(self):
        projects, error = self.__get_all_project_names()
        embedstructure = {}

        if projects is not None:
            #erstellt eine liste mit allen issues eines users
            list = []  
            count = 0
            for i in range(0, len(projects)):
                issues, error = self.__api_get_all_issues_by_project(projects[i])
                if issues is not None:
                    for issue in issues:
                        data = jiradatabase()
                        data._create_connection()
                        if (issue["fields"]["assignee"] != None) and (issue["fields"]["assignee"]["accountId"] == data.get_user_jiraaccountid(self.userid)):
                            list.append(issue["key"])
                            count += 1
                else:
                    return {
                        "title": "ERROR",
                        "description": f"{error} or no projects have been assigned to the user",
                        "color": COLOR_RED
                    }
            #sucht alle projekte der issues raus
            projects = []
            for key in list:
                issue, error = self.__api_get_issue_by_key(key)
                if issue is not None and issue["fields"]["project"]["key"] not in projects:
                    projects.append(issue["fields"]["project"]["key"] + ": " + issue["fields"]["project"]["name"])
            delimiter = " ,"
            projectnames = delimiter.join(projects)
            fields = {
                "projects": projectnames
            }
            embedstructure = {
                    "title": f"Projects from <@!{self.userid}>",
                    "description": f"{len(projects)} running projects",
                    "fields": fields,
                    "color": COLOR_BLUE
                }  
        else:
            embedstructure = {
                    "title": "ERROR",
                    "description": f"{error} or no project exists",
                    "color": COLOR_RED
                }

        return embedstructure


    #übergibt alle Issuenamen als Dictionary für ein Embed
    def get_issues_by_user(self):
        projects, error = self.__get_all_project_names()
        if projects is not None:
            list = []
            count = 0
            for i in range(0, len(projects)):
                issues, error = self.__api_get_all_issues_by_project(projects[i])
                if issues is not None:
                    for issue in issues:
                        data = jiradatabase()
                        if (issue["fields"]["assignee"] != None) and (issue["fields"]["assignee"]["accountId"] == data.get_user_jiraaccountid(self.userid)):
                            list.append((issue["key"] + ":" + issue["fields"]["summary"]))
                            count += 1
                else:
                    return {
                    "title": "ERROR",
                    "description": f"{error} or no Projects exist",
                    "color": COLOR_RED
                }
            delimiter = " ,"
            issuenames = delimiter.join(list)

            fields = {
                "Issues": issuenames
            }
            embedstructure = {
                    "title": f"Issues from <@!{self.userid}>",
                    "description": f"{count} remaining issues",
                    "fields": fields,
                    "color": COLOR_BLUE
                }  
        else:
            embedstructure = {
                    "title": "ERROR",
                    "description": f"{error} or no Projects exist",
                    "color": COLOR_RED
                }
        return embedstructure

    #übergibt die Details von einem Issue, über dem Keynamen des Issue, als Dictionary, für ein Embed
    def get_issue_details(self, key):
        issue, error = self.__api_get_issue_by_key(key)
        embedstructure = {}
        fields = {}
        if issue is not None:
            key = issue["key"]
            if issue["fields"]["assignee"] != None:
                assignee = str(issue["fields"]["assignee"]["displayName"])
            else:
                assignee = "None"
            descriptions = []
            if issue["fields"]["description"] != None:
                for line in issue["fields"]["description"]["content"]:
                    for line2 in line["content"]:
                        if line2["type"] == "text":
                            descriptions.append(line2["text"])
            __created = str(issue["fields"]["created"])
            c_strptime, uselessmilliseconds = __created.split(".")
            __created = str(issue["fields"]["updated"])
            u_strptime, uselessmilliseconds = __created.split(".")

            fields = {
                "project": str(issue["fields"]["project"]["key"]),
                "projecttype": str(issue["fields"]["project"]["projectTypeKey"]),
                "issuetype": str(issue["fields"]["issuetype"]["name"]),
                "status": str(issue["fields"]["status"]["name"]),
                "priority": str(issue["fields"]["priority"]["name"]),
                "created":f'<t:{round(datetime.strptime(c_strptime,"%Y-%m-%dT%H:%M:%S").timestamp())}>',
                "lastUpdate":f'<t:{round(datetime.strptime(u_strptime,"%Y-%m-%dT%H:%M:%S").timestamp())}>',
                "duedate": f'<t:{round(datetime.strptime(issue["fields"]["duedate"],"%Y-%m-%d").timestamp())}>',
                "assignee": assignee,
                "descriptions": descriptions,
                "link": f"https://{self.domain}.atlassian.net/browse/{key}"   #!
            }
            embedstructure = {
                "title": key + ": " + str(issue["fields"]["summary"]),
                "description": None,
                "fields": fields,
                "color": COLOR_BLUE

            }
        else:
            embedstructure = {
                "title": "Error",
                "description": f"{error} or no such issue exists",
                "color": COLOR_RED
                }
        return embedstructure

    #API Anfrage - schreibt einen Kommentar über POST zu einem Issue
    def api_comment_on(self, issuekey, comment):
        url = f"https://{self.domain}.atlassian.net/rest/api/3/issue/{issuekey}/comment"

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        payload = json.dumps( {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                    "type": "paragraph",
                    "content": [
                        {
                        "text": comment,
                        "type": "text"
                        }
                    ]
                    }
                ]
            }
        } )

        response = requests.request(
            "POST",
            url,
            data=payload,
            headers=headers,
            auth=self.auth
        )

        if response.status_code == 201:
            embedstructure = {
                "title": "Successfully commented!",
                "description": f"comment: {comment}",
                "color": COLOR_GREEN

            }
            return embedstructure

        elif response.status_code == 401:
            embedstructure = {
                "title": "ERROR",
                "description": "Authentication credentials are incorrect!",
                "color": COLOR_RED
            }

        elif response.status_code == 404:
            embedstructure = {
                "title": "ERROR",
                "description": "The issue is not found or the user does not have permission to view it",
                "color": COLOR_RED
            }
        else:
            return {
                "title": "UNKNOWN ERROR",
                "color": COLOR_RED
            }