from crewai import Agent
from ci_agent_package.tools.nav_to_building_tool import NavigateToBuildingTool
from ci_agent_package.tools.req_building_nav_tool import RequestBuildingNavigationTool
from ci_agent_package.tools.nav_to_host_tool import NavigateToHostTool
from ci_agent_package.tools.nav_back_to_entrance_tool import NavigateBackToEntranceTool
from ci_agent_package.tasks.escort_to_entrance import EscortToEntranceTask
from ci_agent_package.tasks.escort_to_host import EscortToHostTask


class CIAgent:
    def __init__(self, publisher, subscriber, agent_id, callback_group):
        # Initialize the tools
        self.publisher = publisher
        self.subscriber = subscriber
        self.agent_id = agent_id
        self.available = True
        self.position = 'Entrance'

        # Tools for navigation
        self.navigate_to_building_tool = NavigateToBuildingTool(publisher)
        self.request_building_navigation_tool = RequestBuildingNavigationTool(publisher, subscriber)
        self.navigate_to_host_tool = NavigateToHostTool()
        self.navigate_back_to_entrance_tool = NavigateBackToEntranceTool()

        # Attach tools to the agent
        tools = [
            self.navigate_to_building_tool,
            self.request_building_navigation_tool,
            self.navigate_to_host_tool,
            self.navigate_back_to_entrance_tool
        ]

        # Initialize the agent in CrewAI
        self.agent = Agent(
            role='Campus Incharge',
            goal='Escort visitors to the designated building and host',
            backstory="You're responsible for guiding visitors from the campus entrance to the host and then back to the entrance.",
            memory=False,
            verbose=True,
            tools=tools
        )
    
    def set_available(self):
        self.available = True
        self.position = 'Entrance'
    
    def set_unavailable(self):
        self.available = False
    
    def is_available(self):
        return self.available

    def update_navigation_path(self, navigation_path):
        """
        Update the navigation path inside the RequestBuildingNavigationTool.
        """
        print(f"Updating navigation path: {navigation_path}")
        self.request_building_navigation_tool.set_navigation_path(navigation_path)

    def define_tasks(self):
        """
        Define tasks such as escorting the visitor to the host and back to the entrance.
        """
        escort_to_host_task = EscortToHostTask(agent=self.agent)
        escort_to_entrance_task = EscortToEntranceTask(agent=self.agent)

        return [escort_to_host_task, escort_to_entrance_task]

    def guide_visitor(self, visitor_id, building, room, host):
        """
        Guide the visitor to the building, host, and back to the entrance.
        """
        tasks = self.define_tasks()
        
        result1 = tasks[0].execute(inputs={'agent_id': self.agent_id, 'visitor_id': visitor_id, 'building_id': building, 'room': room, 'host': host, 'navigation_path': None})
        result2 = tasks[1].execute(inputs={'agent_id': self.agent_id, 'visitor_id': visitor_id, 'building_id': building, 'room': room, 'host': host, 'navigation_path': result1})