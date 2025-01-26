from pytm import (
    TM,
    Actor,
    Boundary,
    Classification,
    Data,
    Dataflow,
    Datastore,
    Lambda,
    Server,
    DatastoreType,
)

tm = TM("API Backend Service Threat Model")
tm.description = "This threat model outlines an API communicating with backend services. The API receives requests from users, processes them, and interacts with various backend services for data storage and retrieval."
tm.isOrdered = True
tm.mergeResponses = True
tm.assumptions = [
    "The API is accessible over the internet and interacts with backend services securely.",
]

internet = Boundary("Internet")

api_boundary = Boundary("API Gateway")
api_boundary.levels = [2]

backend_service_boundary = Boundary("Backend Services")
backend_service_boundary.levels = [2]

user = Actor("User")
user.inBoundary = internet
user.levels = [2]

api_server = Server("API Server")
api_server.OS = "Ubuntu"
api_server.controls.isHardened = True
api_server.controls.sanitizesInput = True
api_server.controls.encodesOutput = True
api_server.controls.authorizesSource = True
api_server.sourceFiles = ["api/main.py", "api/docs.md"]

user_requests = Data(
    "User requests to the API", classification=Classification.PUBLIC
)
user_to_api = Dataflow(user, api_server, "User sends request to API (*)")
user_to_api.protocol = "HTTP"
user_to_api.dstPort = 80
user_to_api.data = user_requests
user_to_api.note = "This allows users to interact with the API."

response_data = Data(
    "API response data", classification=Classification.PUBLIC
)
api_to_user = Dataflow(api_server, user, "API responds to the user (*)")
api_to_user.protocol = "HTTP"
api_to_user.data = response_data
api_to_user.responseTo = user_to_api

backend_service = Datastore("Backend Database")
backend_service.OS = "CentOS"
backend_service.controls.isHardened = True
backend_service.inBoundary = backend_service_boundary
backend_service.type = DatastoreType.SQL
backend_service.inScope = True
backend_service.maxClassification = Classification.RESTRICTED
backend_service.levels = [2]

query_data = Data(
    "Query data for processing", classification=Classification.PUBLIC
)
api_to_db = Dataflow(api_server, backend_service, "API sends data to backend DB")
api_to_db.protocol = "MySQL"
api_to_db.dstPort = 3306
api_to_db.data = query_data
api_to_db.note = "This sends relevant data to the database for processing."

retrieved_data = Data(
    "Data retrieved from backend services", classification=Classification.PUBLIC
)
db_to_api = Dataflow(backend_service, api_server, "Backend DB retrieves data for API")
db_to_api.protocol = "MySQL"
db_to_api.dstPort = 3306
db_to_api.data = retrieved_data
api_to_db.responseTo = api_to_db

if __name__ == "__main__":
    tm.process()