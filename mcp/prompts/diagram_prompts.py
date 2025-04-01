"""
MCP prompts templates for diagram generation
"""
import logging
from mcp.server.fastmcp_wrapper import FastMCP

logger = logging.getLogger(__name__)

def register_diagram_prompts(server: FastMCP):
    """
    Register diagram prompts with the MCP server
    
    Args:
        server: The MCP server instance
    """
    logger.info("Registering diagram prompts")
    
    @server.prompt("class_diagram")
    def class_diagram_prompt():
        """Prompt for generating UML class diagrams"""
        return """
Please help me create a class diagram using PlantUML. Include:

1. Classes with attributes and methods
2. Relationships between classes (association, inheritance, composition)
3. Access modifiers for attributes and methods (+public, -private, #protected)

Example:
```plantuml
@startuml
class User {
  -id: int
  -name: string
  -email: string
  +register(): void
  +login(): boolean
}

class Order {
  -id: int
  -date: Date
  -total: float
  +calculateTotal(): float
  +addItem(item: OrderItem): void
}

class OrderItem {
  -quantity: int
  -price: float
  +calculateSubtotal(): float
}

User "1" -- "many" Order
Order "1" *-- "many" OrderItem
@enduml
```
"""

    @server.prompt("sequence_diagram")
    def sequence_diagram_prompt():
        """Prompt for generating UML sequence diagrams"""
        return """
Please help me create a sequence diagram using PlantUML. Include:

1. Participants/actors in the sequence
2. Messages between participants with clear direction
3. Lifelines and activation boxes where appropriate
4. Optional: Notes, conditional logic, loops

Example:
```plantuml
@startuml
actor User
participant "Web Browser" as Browser
participant "Web Server" as Server
database "Database" as DB

User -> Browser: Enter credentials
activate Browser
Browser -> Server: POST /login
activate Server
Server -> DB: Validate credentials
activate DB
DB --> Server: Authentication result
deactivate DB

alt successful login
    Server --> Browser: 200 OK + Session token
    Browser --> User: Show dashboard
else failed login
    Server --> Browser: 401 Unauthorized
    Browser --> User: Show error message
end
deactivate Server
deactivate Browser
@enduml
```
"""

    @server.prompt("activity_diagram")
    def activity_diagram_prompt():
        """Prompt for generating UML activity diagrams"""
        return """
Please help me create an activity diagram using PlantUML. Include:

1. Start and end points
2. Activities/actions
3. Decision points with conditions
4. Transitions between activities
5. Optional: Swim lanes for organizing activities by actor/system

Example:
```plantuml
@startuml
start
:User submits login form;
if (Valid credentials?) then (yes)
  :Generate session token;
  :Load user preferences;
  :Redirect to dashboard;
else (no)
  :Increment failed attempts;
  if (Failed attempts > 3?) then (yes)
    :Lock account;
    :Send security alert;
  else (no)
    :Show error message;
  endif
  :Redirect to login page;
endif
stop
@enduml
```
"""

    logger.info("Diagram prompts registered successfully")
