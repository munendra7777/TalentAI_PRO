from crewai_tools import BaseTool
from .client import Client as LinkedinClient

class LinkedInTool(BaseTool):
    name: str = "Retrieve LinkedIn profiles"
    description: str = (
        "Retrieve LinkedIn profiles given a list of skills. Comma separated"
    )

    def _run(self, skills: str) -> str:
        linkedin_client = LinkedinClient()
        people = linkedin_client.find_people(skills)
        linkedin_client.close()
        return self._format_people_to_json(people)

    def _format_people_to_json(self, people):
        result = [
            {
                "name": p['name'],
                "position": p['position'],
                "location": p['location'],
                "profile_link": p["profile_link"]
            }
            for p in people
        ]
        return result